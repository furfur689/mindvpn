package main

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"

	"mindvpn/agent/internal/agent"
	"mindvpn/agent/internal/config"
	"mindvpn/agent/internal/metrics"
)

var (
	cfgFile string
	rootCmd = &cobra.Command{
		Use:   "mind-agent",
		Short: "MindVPN Node Agent",
		Long:  `MindVPN Node Agent - управляет VPN сервисами на узле`,
		RunE:  run,
	}
)

func init() {
	cobra.OnInitialize(initConfig)

	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.mind-agent.yaml)")
	rootCmd.PersistentFlags().String("cp-url", "https://cp.mindvpn.local", "Control Plane URL")
	rootCmd.PersistentFlags().String("node-id", "", "Node ID")
	rootCmd.PersistentFlags().String("labels", "", "Node labels (comma-separated)")
	rootCmd.PersistentFlags().String("cert-path", "/etc/mindvpn/agent.crt", "Agent certificate path")
	rootCmd.PersistentFlags().String("key-path", "/etc/mindvpn/agent.key", "Agent private key path")
	rootCmd.PersistentFlags().String("ca-path", "/etc/mindvpn/ca.crt", "CA certificate path")
	rootCmd.PersistentFlags().Int("metrics-port", 9101, "Metrics server port")
	rootCmd.PersistentFlags().Bool("mock", false, "Run in mock mode")

	viper.BindPFlag("cp_url", rootCmd.PersistentFlags().Lookup("cp-url"))
	viper.BindPFlag("node_id", rootCmd.PersistentFlags().Lookup("node-id"))
	viper.BindPFlag("labels", rootCmd.PersistentFlags().Lookup("labels"))
	viper.BindPFlag("cert_path", rootCmd.PersistentFlags().Lookup("cert-path"))
	viper.BindPFlag("key_path", rootCmd.PersistentFlags().Lookup("key-path"))
	viper.BindPFlag("ca_path", rootCmd.PersistentFlags().Lookup("ca-path"))
	viper.BindPFlag("metrics_port", rootCmd.PersistentFlags().Lookup("metrics-port"))
	viper.BindPFlag("mock", rootCmd.PersistentFlags().Lookup("mock"))
}

func initConfig() {
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		home, err := os.UserHomeDir()
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		viper.AddConfigPath(home)
		viper.AddConfigPath(".")
		viper.SetConfigType("yaml")
		viper.SetConfigName(".mind-agent")
	}

	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err == nil {
		fmt.Println("Using config file:", viper.ConfigFileUsed())
	}
}

func run(cmd *cobra.Command, args []string) error {
	// Загружаем конфигурацию
	cfg := &config.Config{
		CPURL:      viper.GetString("cp_url"),
		NodeID:     viper.GetString("node_id"),
		Labels:     viper.GetString("labels"),
		CertPath:   viper.GetString("cert_path"),
		KeyPath:    viper.GetString("key_path"),
		CAPath:     viper.GetString("ca_path"),
		MetricsPort: viper.GetInt("metrics_port"),
		Mock:       viper.GetBool("mock"),
	}

	// Валидируем конфигурацию
	if err := cfg.Validate(); err != nil {
		return fmt.Errorf("invalid config: %w", err)
	}

	// Инициализируем метрики
	metrics.Init()

	// Создаем агента
	agent, err := agent.New(cfg)
	if err != nil {
		return fmt.Errorf("failed to create agent: %w", err)
	}

	// Запускаем метрики сервер
	go startMetricsServer(cfg.MetricsPort)

	// Запускаем агента
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Обработка сигналов для graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		log.Println("Received shutdown signal, stopping agent...")
		cancel()
	}()

	// Запускаем агента
	if err := agent.Run(ctx); err != nil {
		return fmt.Errorf("agent failed: %w", err)
	}

	return nil
}

func startMetricsServer(port int) {
	router := gin.Default()
	
	// Prometheus metrics endpoint
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))
	
	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "healthy",
			"service": "mind-agent",
			"timestamp": time.Now().Unix(),
		})
	})

	log.Printf("Starting metrics server on port %d", port)
	if err := router.Run(fmt.Sprintf(":%d", port)); err != nil {
		log.Fatalf("Failed to start metrics server: %v", err)
	}
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
