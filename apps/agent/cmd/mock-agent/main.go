package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/spf13/cobra"
)

var (
	nodeID   string
	labels   string
	port     int
	rootCmd  = &cobra.Command{
		Use:   "mock-agent",
		Short: "MindVPN Mock Agent",
		Long:  `Mock агент для тестирования MindVPN Control Plane`,
		RunE:  run,
	}
)

func init() {
	rootCmd.PersistentFlags().StringVar(&nodeID, "node-id", "mock-node", "Node ID")
	rootCmd.PersistentFlags().StringVar(&labels, "labels", "region=EU,provider=hetzner", "Node labels")
	rootCmd.PersistentFlags().IntVar(&port, "port", 9101, "Metrics port")
}

// Mock метрики
var (
	cpuUsage = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "mindvpn_node_cpu_usage_percent",
		Help: "CPU usage percentage",
	})
	memoryUsage = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "mindvpn_node_memory_usage_percent",
		Help: "Memory usage percentage",
	})
	usersOnline = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "mindvpn_node_users_online",
		Help: "Number of online users",
	})
	tasksProcessed = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "mindvpn_node_tasks_processed_total",
		Help: "Total number of tasks processed",
	})
	heartbeatsSent = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "mindvpn_node_heartbeats_sent_total",
		Help: "Total number of heartbeats sent",
	})
)

func run(cmd *cobra.Command, args []string) error {
	// Регистрируем метрики
	prometheus.MustRegister(cpuUsage, memoryUsage, usersOnline, tasksProcessed, heartbeatsSent)

	// Парсим labels
	labelMap := make(map[string]string)
	for _, label := range strings.Split(labels, ",") {
		if parts := strings.SplitN(label, "=", 2); len(parts) == 2 {
			labelMap[parts[0]] = parts[1]
		}
	}

	log.Printf("Starting mock agent: node-id=%s, labels=%v, port=%d", nodeID, labelMap, port)

	// Создаем HTTP сервер
	router := gin.Default()

	// Prometheus metrics
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "healthy",
			"service":   "mock-agent",
			"node_id":   nodeID,
			"labels":    labelMap,
			"timestamp": time.Now().Unix(),
		})
	})

	// API endpoints для имитации агента
	router.POST("/api/v1/register", func(c *gin.Context) {
		// Имитируем регистрацию
		c.JSON(http.StatusOK, gin.H{
			"node_id": nodeID,
			"status":  "registered",
			"config": gin.H{
				"cp_url":  "https://cp.mindvpn.local",
				"node_id": nodeID,
			},
		})
	})

	router.POST("/api/v1/heartbeat", func(c *gin.Context) {
		// Имитируем heartbeat
		heartbeatsSent.Inc()
		
		// Генерируем случайные метрики
		cpuUsage.Set(rand.Float64() * 100)
		memoryUsage.Set(rand.Float64() * 100)
		usersOnline.Set(float64(rand.Intn(100)))

		c.JSON(http.StatusOK, gin.H{
			"status": "ok",
			"metrics": gin.H{
				"cpu_usage":    cpuUsage.Get(),
				"memory_usage": memoryUsage.Get(),
				"users_online": int(usersOnline.Get()),
			},
		})
	})

	router.POST("/api/v1/tasks/:task_id/apply", func(c *gin.Context) {
		taskID := c.Param("task_id")
		tasksProcessed.Inc()

		// Имитируем обработку задачи
		time.Sleep(time.Duration(rand.Intn(2000)) * time.Millisecond)

		// 90% успешных задач
		success := rand.Float64() > 0.1

		if success {
			c.JSON(http.StatusOK, gin.H{
				"task_id": taskID,
				"status":  "success",
				"message": "Task applied successfully",
			})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{
				"task_id": taskID,
				"status":  "failed",
				"message": "Task failed",
			})
		}
	})

	// Запускаем сервер
	go func() {
		addr := fmt.Sprintf(":%d", port)
		log.Printf("Starting mock agent server on %s", addr)
		if err := router.Run(addr); err != nil {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Обработка сигналов
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	<-sigChan
	log.Println("Shutting down mock agent...")

	return nil
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
