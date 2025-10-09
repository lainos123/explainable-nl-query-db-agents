# Architecture Diagrams

This document contains Mermaid diagrams describing the architecture of the Explainable NL Query DB Agents application.

## 1. System Architecture Overview

```mermaid
graph TB
    %% Frontend Layer
    subgraph "Frontend (Next.js - Port 3001)"
        UI[User Interface]
        Chat[Chatbot Interface]
        Settings[Settings Page]
        FileView[File View Page]
        Results[Results Page]
    end

    %% Backend Layer
    subgraph "Backend (Django - Port 8000)"
        API[Django REST API]
        
        subgraph "Core Modules"
            CoreViews[Core Views]
            Models[Models]
            Auth[Authentication]
            Storage[File Storage]
        end

        subgraph "Agent Pipeline"
            DBSelect[A: DB Select Agent]
            TableSelect[B: Table Select Agent]
            SQLGen[C: SQL Generate Agent]
            SQLConn[D: SQL Connector]
        end

        subgraph "Utilities"
            SchemaBuilder[Schema Builder]
            SQLConnector[SQL Connector]
        end
    end

    %% External Services
    subgraph "External"
        DB[(Database Files)]
        AI[AI API Service]
        FileSystem[File System]
    end

    %% Connections
    UI --> API
    Chat --> API
    Settings --> API
    FileView --> API
    Results --> API

    API --> CoreViews
    CoreViews --> Models
    CoreViews --> Auth
    CoreViews --> Storage

    API --> DBSelect
    DBSelect --> TableSelect
    TableSelect --> SQLGen
    SQLGen --> SQLConn

    SchemaBuilder --> FileSystem
    SQLConnector --> DB
    SQLGen --> AI
    Storage --> FileSystem

    %% Styling
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
    classDef agent fill:#fff3e0
    classDef external fill:#e8f5e8

    class UI,Chat,Settings,FileView,Results frontend
    class API,CoreViews,Models,Auth,Storage backend
    class DBSelect,TableSelect,SQLGen,SQLConn agent
    class DB,AI,FileSystem external
```

## 2. Agent Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant DBSelect as A: DB Select
    participant TableSelect as B: Table Select  
    participant SQLGen as C: SQL Generate
    participant SQLConn as D: SQL Connector
    participant Database
    participant AIService as AI API

    User->>Frontend: Enter natural language question
    Frontend->>API: POST /api/agents/run_pipeline/
    
    Note over API: Start Agent Pipeline
    
    API->>DBSelect: Select appropriate database
    DBSelect-->>API: Database selected
    
    API->>TableSelect: Select relevant tables
    TableSelect-->>API: Table list
    
    API->>SQLGen: Generate SQL query
    SQLGen->>AIService: Call AI to generate SQL
    AIService-->>SQLGen: SQL query
    SQLGen-->>API: SQL generated
    
    API->>SQLConn: Execute SQL
    SQLConn->>Database: Run query
    Database-->>SQLConn: Results
    SQLConn-->>API: Data returned
    
    API-->>Frontend: Stream results in real-time
    Frontend-->>User: Display results
```

## 3. Component Structure

```mermaid
graph TD
    %% Frontend Components
    subgraph "Frontend Components"
        App[app/layout.tsx]
        
        subgraph "Pages"
            HomePage[page.tsx]
            ChatbotPage[chatbot/page.tsx]
            SettingsPage[settings/page.tsx]
            FilesPage[view-files/page.tsx]
            ResultPage[result/page.tsx]
        end

        subgraph "Chatbot Components"
            ChatBox[chatbox.tsx]
            InsertBox[insert_box.tsx]
            Menu[menu.tsx]
            MobileMenu[mobile_menu.tsx]
            ChatLogic[chatbot_logic.tsx]
            StreamLogic[streaming_logic.ts]
        end

        subgraph "Services"
            APIService[api.ts]
            AuthService[auth.ts]
            ConfigService[config.ts]
            FetchService[fetch.ts]
            SSEService[sse.ts]
        end

        subgraph "File Management"
            FileActions[file_actions.tsx]
            FileTable[file_table.tsx]
        end
    end

    %% Backend Modules
    subgraph "Backend Modules"
        subgraph "Core App"
            CoreModels[models.py]
            CoreViews[views.py]
            CoreAdmin[admin.py]
            APIChat[api_chat.py]
            APIStorage[api_storage.py]
            Serializers[serializers.py]
        end

        subgraph "Agents App"
            AgentViews[agents/views.py]
            AgentA[a_db_select.py]
            AgentB[b_table_select.py]
            AgentC[c_sql_generate.py]
            AgentTest[test.py]
        end

        subgraph "Configuration"
            Settings[config/settings.py]
            URLs[config/urls.py]
            WSGI[wsgi.py]
            ASGI[asgi.py]
        end

        subgraph "Utils"
            SchemaBuilder[schema_builder.py]
            SQLConnector[sql_connector.py]
        end
    end

    %% Connections
    App --> HomePage
    App --> ChatbotPage
    App --> SettingsPage
    App --> FilesPage
    App --> ResultPage

    ChatbotPage --> ChatBox
    ChatbotPage --> InsertBox
    ChatbotPage --> Menu
    ChatbotPage --> MobileMenu
    
    ChatBox --> ChatLogic
    ChatBox --> StreamLogic
    
    ChatLogic --> APIService
    APIService --> AuthService
    APIService --> FetchService
    APIService --> SSEService

    FilesPage --> FileActions
    FilesPage --> FileTable

    AgentViews --> AgentA
    AgentA --> AgentB
    AgentB --> AgentC
    AgentC --> SQLConnector

    CoreViews --> CoreModels
    CoreViews --> Serializers
    APIChat --> CoreModels
    APIStorage --> CoreModels

    %% Styling
    classDef page fill:#e3f2fd
    classDef component fill:#fff3e0
    classDef service fill:#e8f5e8
    classDef backend fill:#f3e5f5

    class HomePage,ChatbotPage,SettingsPage,FilesPage,ResultPage page
    class ChatBox,InsertBox,Menu,MobileMenu,FileActions,FileTable component
    class APIService,AuthService,ConfigService,FetchService,SSEService service
    class CoreModels,CoreViews,AgentViews,Settings backend
```

## 4. Data Flow Architecture

```mermaid
flowchart TD
    %% User Input
    User[👤 User Input<br/>Natural Language Query]
    
    %% Frontend Processing
    UI[🖥️ Frontend UI<br/>React/Next.js]
    
    %% API Gateway
    API[🌐 Django REST API<br/>Authentication & Routing]
    
    %% Agent Pipeline
    subgraph Pipeline["🤖 Agent Processing Pipeline"]
        A[Agent A<br/>Database Selection]
        B[Agent B<br/>Table Selection]
        C[Agent C<br/>SQL Generation]
        D[Agent D<br/>SQL Execution]
    end
    
    %% External Services
    AIService[🧠 AI Service<br/>LLM API]
    Database[🗄️ Database<br/>SQLite/CSV Files]
    
    %% Data Storage
    subgraph Storage["💾 Data Storage"]
        FileStorage[File Storage<br/>Uploaded DBs]
        UserData[User Data<br/>Chats & Settings]
        Cache[Cache Layer<br/>Agent Results]
    end
    
    %% Results
    Results[📊 Query Results<br/>Structured Data]
    
    %% Flow Connections
    User --> UI
    UI <--> API
    
    API --> Pipeline
    A --> B
    B --> C
    C --> D
    
    C <--> AIService
    D <--> Database
    
    API <--> Storage
    
    Pipeline --> Results
    Results --> UI
    UI --> User
    
    %% Styling
    classDef user fill:#ffcdd2
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
    classDef agent fill:#fff3e0
    classDef external fill:#e8f5e8
    classDef storage fill:#fce4ec
    
    class User user
    class UI frontend
    class API backend
    class A,B,C,D agent
    class AIService,Database external
    class FileStorage,UserData,Cache storage
```

## 5. Database Schema

```mermaid
erDiagram
    USER ||--o{ FILES : uploads
    USER ||--o| CHATS : has
    USER ||--o| APIKEYS : configures
    USER ||--o| USERLIMITS : has
    USER ||--o{ DAILYUSAGE : tracks

    USER {
        int id PK
        string username
        string email
        string password
        datetime date_joined
    }

    FILES {
        int id PK
        int user_id FK
        string database
        file file
        datetime time
        bigint size
    }

    CHATS {
        int id PK
        int user_id FK
        text chats
        datetime time
    }

    APIKEYS {
        int id PK
        int user_id FK
        text api_key
    }

    USERLIMITS {
        int id PK
        int user_id FK
        int max_chats
        int max_gb_db
    }

    DAILYUSAGE {
        int id PK
        int user_id FK
        date date
        int chats_used
    }
```

## 6. Deployment Architecture

```mermaid
graph TB
    %% Container Layer
    subgraph "🐳 Docker Containers"
        Frontend[Frontend Container<br/>Next.js<br/>Port: 3001]
        Backend[Backend Container<br/>Django<br/>Port: 8000]
    end

    %% Volume Mounts
    subgraph "📁 Volume Mounts"
        BackendCode[./backend:/app]
        MediaFiles[backend_media:/app/media]
        DataFiles[../data:/data]
    end

    %% Host System
    subgraph "💻 Host System"
        LocalBackend[./backend/]
        LocalData[../data/]
        LocalMedia[media files]
    end

    %% Network
    subgraph "🌐 Network"
        Port3001[Host:3001]
        Port8000[Host:8000]
    end

    %% External Dependencies
    subgraph "🔗 External Services"
        AIProvider[AI API Provider<br/>OpenAI/Anthropic/etc]
        Files[Database Files<br/>SQLite/CSV]
    end

    %% Connections
    Port3001 --> Frontend
    Port8000 --> Backend
    
    Backend --- BackendCode
    Backend --- MediaFiles
    Backend --- DataFiles
    
    BackendCode --- LocalBackend
    DataFiles --- LocalData
    MediaFiles --- LocalMedia
    
    Backend --> AIProvider
    Backend --> Files
    Frontend --> Backend

    %% Styling
    classDef container fill:#e1f5fe
    classDef volume fill:#fff3e0
    classDef host fill:#e8f5e8
    classDef network fill:#f3e5f5
    classDef external fill:#ffcdd2

    class Frontend,Backend container
    class BackendCode,MediaFiles,DataFiles volume
    class LocalBackend,LocalData,LocalMedia host
    class Port3001,Port8000 network
    class AIProvider,Files external
```

## Architecture Summary

### Technologies Used:
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: Django, Django REST Framework, Python
- **Database**: SQLite (for metadata), CSV/SQLite files (for data)
- **AI Integration**: API calls to LLM services
- **Deployment**: Docker, Docker Compose

### Main Processing Flow

1. User enters natural language question through web interface
2. Frontend sends request to Django REST API
3. Backend runs 4-agent pipeline sequentially:
   - Agent A: Select appropriate database
   - Agent B: Select relevant tables/columns
   - Agent C: Generate SQL query with AI
   - Agent D: Execute SQL and return results
4. Results are streamed back to frontend in real-time
5. User views formatted and explained results

### Key Features

- Chatbot interface with streaming responses
- File upload and database management
- User authentication and rate limiting
- API key management for AI services
- Real-time query explanation and results
