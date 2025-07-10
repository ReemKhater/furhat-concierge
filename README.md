# Furhat Concierge

A Dockerized AI assistant for Furhat robots featuring:
- Natural language processing via Ollama 
- Document-based responses using LangChain RAG
- Multi-environment support (virtual/physical robots)
- Conversation logging

A project made during my internship at the LifeSTech research group at UPM, Madrid. 

## Table of Contents
- [Requirements](#requirements)
- [Deployment](#deployment)
- [Features](#features)
- [Development](#development)
- [Contributors](#contributors)

## Requirements
### Core Dependencies
- Python 3.10.11
- Docker server: https://docker.lst.tfo.upm.es/
- Ollama server: http://tinman.lst:11434

### Environment Specific
| Environment | Requirements |
|-------------|-------------|
| **Physical Robot** | Furhat OS |
| **Virtual Robot** | Furhat SDK 2.8.3 and Docker Desktop |
| **LST Network** | VPN access |

## File structure 
```bash 
├── Knowledge/          # PDF knowledge base
├── chroma_db/          # Vector store (auto-generated)
├── main.py             # Core application
├── Dockerfile          # Container configuration
├── .gitlab-ci.yml      # Multi-container setup
└── requirements.txt    # Python dependencies
```

## Deployment 

Docker images are automatically built via .gitlab-ci.yml. 

### Physical Robot Setup

1. Run DNS to acces robot interface: http://furhat.robot.ll.lst/#/ 
    - Password : admin 
2. Start Remote API Skill 
3. Verify robot IP (default: 192.168.0.80)

### Virtual Robot Setup

1. Run Furhat SDK and launch virtual Furhat
2. Start Remote API Skill 
3. Open web interface (localhost:8080) 
    - Password: admin
4. Commit IP address of your computer in .env file
5. Open Docker Desktop and run the following commands in the terminal: 

```bash 
docker login https://gitlab.lst.tfo.upm.es/ # login with LST credentials (use personal access token with read_registery scope for the password)

docker pull gitlab.lst.tfo.upm.es:4567/lifespace/robots/furhat-concierge:latest # pull latest generated image from Docker LST instance to run it locally 

docker run -it `
    --network=host `
    -e FURHAT_HOST=192.168.1.101 ` #replace with IP address of your computer
    gitlab.lst.tfo.upm.es:4567/lifespace/robots/furhat-concierge:latest
```

## Features 

1. Natural Conversation

Through the implementation of the Ollama LLM intelligence, the robot holds conversational interactions with users. 

2. Knowledge Base 

The robot can answer questions on these specific topics: 

    - UPM (Universidad Politécnica de Madrid)
    - ETSIT (School of Telecommunications Engineering)
    - The LST research group and its projects (Gatekeeper, Activage, Pharmaledger, Better@home, Gravitate Health, Plan4Act, Odin, Vitalise, Brainteaser, ToLife, Protect Child, BD4QoL, Improve, IDEA4RC)
    - The Living Lab facilities

3. Conversation Logs

Access conversation logs through: https://furhat-logs.d.lst.tfo.upm.es/

    - Username: admin 
    - Password: generated in the logs of the furhat-logs container through https://docker.lst.tfo.upm.es/ 

The logs are saved in text files given in the following format:
    
```bash 
[TIMESTAMP] USER: Hello  
[TIMESTAMP] ROBOT: Hi there!  
```

4. Accessible Basic Development 

The Ollama model and the voice for Furhat can both be easily modified through the .env file. The environment variables are set as such: 

```bash 
OLLAMA_MODEL=gemma2:27b

# Robot voices 
VOICE_EN=Matthew  # English voice
VOICE_ES=Enrique  # Spanish voice  
VOICE_FR=Mathieu  # French voice 
```

Check the available Ollama models on tinman.lst and the available voices in the settings of the Furhat DNS. 

## Development 

### LST Development 

1. Clone and setup
```bash
git clone https://gitlab.lst.tfo.upm.es/lifespace/robots/furhat-concierge
cd furhat-concierge
```

2. Use pre-configured CI/CD
- Push to `pilot` branch for auto-testing
- Merge to `main` for deployment

3. Access resources:
- Ollama: http://tinman.lst:11434
- Logs: https://furhat-logs.d.lst.tfo.upm.es/
- Docker: https://docker.lst.tfo.upm.es/ 

### Local Development 

It is possible to work locally on this project, without the LST infrastucture. 

1. Ollama Setup

```bash
# Download Ollama from https://ollama.com/ and pull desired model
ollama serve
ollama pull gemma3 
```

```bash 
# Modify Ollama setup in main script
llm = Ollama(model="gemma3")
```

2. Python Setup
``` bash
python -m ollama .venv
ollama\Scripts\activate    
pip install -r requirements.txt
```

3. Configuration

```bash 
# Edit .env:
IP_ADDRESS=localhost # Uncomment and set to "localhost"
```

4. Run with Docker Desktop
``` bash
docker build -t furhat-local .
docker run -it furhat-local
```

## Contributors 

### Core Team 

| Role | Name | Contribution Area 
|-------------|-------------|-------------|
|**Internship Supervisor** | Dr. Alejandro Medrano Gil | Project guidance & architecture
| **PhD Supervisor** | Dr. Ivana Lombroni | Research methodology
| **LST Robotics Team** |  | Knowledge base & tests 

### Institutional Partners

- **Living Lab Technologies**  
  Provided Furhat infrastructure and testing facilities
- **UPM ETSIT**  
  Academic oversight 




