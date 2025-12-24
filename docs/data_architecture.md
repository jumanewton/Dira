# Dira Data Architecture


## Current Heroku Setup

```
dira-platform-backend (Heroku App)
├── JAC Graph Database: main.session (in-memory + file)
├── PostgreSQL: Provisioned but UNUSED
├── Weaviate: NOT CONNECTED
└── Services Running:
    ├── JAC Server (port 8000) - Main API
    └── NLP Service (port 8001) - AI/ML operations
```

```
dira-platform-frontend (Heroku App)
└── React Static Files served by `serve`
```

---

