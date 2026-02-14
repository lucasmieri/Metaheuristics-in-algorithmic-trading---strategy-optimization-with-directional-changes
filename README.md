# start new project, metah to dc strategies.

dc_trading_research/
│
├── main.ipynb                          # Notebook principal para experimentos
├── requirements.txt                    # Dependências do projeto
├── README.md                          # Documentação do projeto
│
├── config/
│   ├── __init__.py
│   ├── parametros.py                  # Dicionário centralizado de parâmetros
│   └── paths.py                       # Caminhos padronizados do projeto
│
├── data/
│   ├── raw/                           # Dados brutos (*.gzip)
│   ├── processed/                     # Dados processados
│   └── cache/                         # Cache temporário
│
├── logs/
│   └── .gitkeep                       # Logs gerados automaticamente
│
├── results/
│   ├── experiments/                   # Resultados dos experimentos
│   ├── figures/                       # Gráficos e visualizações
│   └── tables/                        # Tabelas para o paper
│
├── src/
│   ├── __init__.py
│   │
│   ├── dc_model_manager.py           # Hub central do sistema
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger_setup.py           # Configuração do sistema de logging
│   │   └── file_utils.py             # Utilitários para manipulação de arquivos
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_collector.py         # Coleta de dados com cache
│   │   ├── data_validator.py         # Validação de dados
│   │   └── data_preprocessor.py      # Pré-processamento
│   │
│   ├── dc/
│   │   ├── __init__.py
│   │   ├── dc_transformer.py         # Transformação para DC
│   │   ├── dc_indicators.py          # Indicadores baseados em DC
│   │   └── dc_events.py              # Detecção de eventos DC
│   │
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base_strategy.py          # Classe base para estratégias
│   │   ├── dc_strategy.py            # Estratégias baseadas em DC
│   │   └── signal_generator.py       # Geração de sinais de trading
│   │
│   ├── optimization/
│   │   ├── __init__.py
│   │   ├── genetic_algorithm.py      # Implementação GA
│   │   ├── particle_swarm.py         # Implementação PSO
│   │   ├── hybrid_optimizer.py       # GA-PSO híbrido
│   │   └── fitness_functions.py      # Funções objetivo multi-objetivo
│   │
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── backtest_engine.py        # Motor de backtesting
│   │   ├── transaction_costs.py      # Modelagem de custos
│   │   └── performance_metrics.py    # Métricas de performance
│   │
│   └── analysis/
│       ├── __init__.py
│       ├── statistical_tests.py      # Testes estatísticos
│       ├── visualization.py          # Visualizações
│       └── report_generator.py       # Geração de relatórios
│
└── tests/
    ├── __init__.py
    ├── test_data_collector.py
    ├── test_dc_transformer.py
    └── test_optimization.py