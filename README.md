<p align="center">
  <a href="https://portofolio.vzkyrielight.xyz">
    <img src="assets/banner.svg" width="100%" alt="Farhan Taufik Rahman, Software Engineer working in Java and Go. I build full-stack systems, then keep them running." />
  </a>
</p>

<p align="center">
  <a href="https://portofolio.vzkyrielight.xyz"><img src="https://img.shields.io/badge/Portofolio-vzkyrielight.xyz-ffb524?style=for-the-badge&labelColor=070b22" alt="Portofolio" /></a>
  <a href="https://www.linkedin.com/in/farhan-taufik-rahman/"><img src="https://img.shields.io/badge/LinkedIn-Connect-5b7cff?style=for-the-badge&logo=linkedin&logoColor=white&labelColor=070b22" alt="LinkedIn" /></a>
  <a href="mailto:farhanarrahman27@gmail.com"><img src="https://img.shields.io/badge/Email-Say_hello-ecf1ff?style=for-the-badge&logo=gmail&logoColor=white&labelColor=070b22" alt="Email" /></a>
  <a href="https://github.com/farhantaufikrahman?tab=followers"><img src="https://img.shields.io/github/followers/farhantaufikrahman?style=for-the-badge&logo=github&logoColor=white&label=Followers&labelColor=070b22&color=b892ff" alt="GitHub followers" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-open_to_software_engineer_roles-3be38b?style=flat-square&labelColor=070b22" alt="Open to software engineer roles" />
  <img src="https://img.shields.io/badge/available_in-Jabodetabek-8ea6ff?style=flat-square&labelColor=070b22" alt="Available for work in Jabodetabek" />
  <img src="https://img.shields.io/badge/Java-Spring_Boot-ffb524?style=flat-square&logo=openjdk&logoColor=white&labelColor=070b22" alt="Java and Spring Boot" />
  <img src="https://img.shields.io/badge/Go-gRPC-4fe3c1?style=flat-square&logo=go&logoColor=white&labelColor=070b22" alt="Go and gRPC" />
  <img src="https://img.shields.io/badge/Microservices-Kafka_%C2%B7_NATS-ff7ab8?style=flat-square&logo=apachekafka&logoColor=white&labelColor=070b22" alt="Microservices with Kafka and NATS" />
  <img src="https://img.shields.io/badge/CI%2FCD-Jenkins_%C2%B7_GitHub_Actions-5ec8ff?style=flat-square&logo=githubactions&logoColor=white&labelColor=070b22" alt="CI/CD with Jenkins and GitHub Actions" />
  <img src="https://img.shields.io/badge/Orchestration-Kubernetes_%C2%B7_Helm-b892ff?style=flat-square&logo=kubernetes&logoColor=white&labelColor=070b22" alt="Orchestration with Kubernetes and Helm" />
  <img src="https://img.shields.io/badge/AWS-Certified_Cloud_Practitioner-ff9900?style=flat-square&logo=amazonwebservices&logoColor=white&labelColor=070b22" alt="AWS Certified Cloud Practitioner" />
</p>

## 🛰️ Ground control

Software engineer working mainly in **Java** and **Go**, with a focus on **microservices**, **CI/CD** and **container orchestration**. I design, ship, deploy **and monitor** my own systems: Go microservices over gRPC and NATS, Spring Boot services with Kafka, orchestrated on Kubernetes with Helm and Kustomize, released through Jenkins and GitHub Actions pipelines, and watched by Prometheus + Grafana.

Before software, I spent four years in telecom: an Electrical Engineering degree, then network monitoring and incident handling for **SATRIA-1**, Indonesia's national satellite. That is where the "keep them running" habit comes from.

<img src="assets/pipeline.svg" width="100%" alt="How I ship, animated: 01 Code in Java, Go and TypeScript; 02 Commit to GitHub with a pull request; 03 CI/CD with Jenkins, GitHub Actions and SonarQube (build, test, scan); 04 Package as Docker images tagged by SHA; 05 Orchestrate microservices on Kubernetes with Helm and Kustomize; 06 Expose through the Gateway API, Cloudflare and AWS; 07 Observe with Prometheus and Grafana. A failed smoke test rolls back automatically, and alerts feed the next change." />

## 🌌 Missions

Five projects I built and shipped. Each card opens the repository; the buttons under it open the live app.

<a href="https://github.com/farhantaufikrahman/Ice-Stream"><img src="assets/card-ice-stream.svg" width="100%" alt="Mission 01, Ice Stream: a Bilibili-style video and live-streaming platform built as Go microservices on Kubernetes" /></a>

<p align="center">
  <a href="https://icestream.vzkyrielight.my.id"><img src="https://img.shields.io/badge/%E2%96%B6_Live_demo-4fe3c1?style=for-the-badge&labelColor=070b22" alt="Ice Stream live demo" /></a>
  <a href="https://github.com/farhantaufikrahman/Ice-Stream"><img src="https://img.shields.io/badge/Repository-070b22?style=for-the-badge&logo=github&logoColor=white" alt="Ice Stream repository" /></a>
  <a href="https://portofolio.vzkyrielight.xyz/#ice-stream"><img src="https://img.shields.io/badge/Case_study-0e1538?style=for-the-badge&logoColor=white" alt="Ice Stream case study" /></a>
</p>

<a href="https://icestream.vzkyrielight.my.id"><img src="assets/ice-stream.gif" width="100%" alt="Ice Stream showcase: uploading, playback with danmaku, live streaming, Creator Studio and monitoring" /></a>

<details>
<summary><b>🔭 How Ice Stream works</b> &nbsp;(architecture, decisions, Node.js and Java equivalents)</summary>
<br />

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#0e1538','primaryTextColor':'#ecf1ff','primaryBorderColor':'#4fe3c1','lineColor':'#5b7cff','secondaryColor':'#0e1538','tertiaryColor':'#070b22','clusterBkg':'#070b22','clusterBorder':'#26326e','fontFamily':'ui-monospace, monospace'}}}%%
flowchart LR
  viewer([Viewer<br/>React + hls.js]) --> cf[Cloudflare Tunnel]
  creator([Creator<br/>OBS or browser]) -->|RTMP / WHIP| cf
  cf --> gw[Gateway API]
  subgraph k8s [Kubernetes]
    gw --> api[api<br/>Go + Gin]
    gw --> mtx[MediaMTX<br/>RTMP, WHIP, LL-HLS]
    gw --> s3[(RustFS<br/>S3-compatible)]
    api -->|gRPC| auth[auth]
    api -->|gRPC| video[video]
    auth --> ora[(Oracle)]
    video --> ora
    video --> nats{{NATS JetStream}}
    nats -->|SSE fan-out| api
    nats --> tc[transcoder<br/>Go + FFmpeg]
    tc --> s3
    mtx -->|auth hook| video
  end
```

| Problem | Decision |
| --- | --- |
| Multi-gigabyte uploads fail halfway on a home connection | The browser uploads straight to S3-compatible storage in 50 MB parts with presigned URLs; a dropped part retries on its own. |
| A transcode job is lost when the worker restarts | Jobs go through NATS JetStream and stay there until the transcoder acknowledges them: `UPLOADED → PROCESSING → READY` (or `FAILED` with a reason). |
| Danmaku must reach viewers connected to any API pod | VideoService publishes every message on NATS; each gateway pod streams it to its own viewers over Server-Sent Events. |
| Nobody should broadcast on someone else's channel | MediaMTX asks VideoService through an auth hook; stream keys are stored as hashes, browser broadcasts use a 5-minute token. |

> **Coming from Node.js?** The Gin gateway plays the role of an Express app, gRPC interceptors work like Express middleware, and GORM is the Go counterpart of Sequelize or Prisma. In Java, the same shape is Spring Cloud Gateway in front of Spring Boot services that call each other over gRPC.

</details>

<br />

<a href="https://github.com/farhantaufikrahman/Llama-Express"><img src="assets/card-llama-express.svg" width="100%" alt="Mission 02, Llama Express: a real-time courier platform with Spring Boot, Kafka and Kubernetes" /></a>

<p align="center">
  <a href="https://llama.vzkyrielight.my.id"><img src="https://img.shields.io/badge/%E2%96%B6_Live_demo-ffb524?style=for-the-badge&labelColor=070b22" alt="Llama Express live demo" /></a>
  <a href="https://github.com/farhantaufikrahman/Llama-Express"><img src="https://img.shields.io/badge/Repository-070b22?style=for-the-badge&logo=github&logoColor=white" alt="Llama Express repository" /></a>
  <a href="https://portofolio.vzkyrielight.xyz/#llama-express"><img src="https://img.shields.io/badge/Case_study-0e1538?style=for-the-badge&logoColor=white" alt="Llama Express case study" /></a>
</p>

<a href="https://llama.vzkyrielight.my.id"><img src="assets/llama-express.gif" width="100%" alt="30-second tour of Llama Express: customer tracking, courier app, public tracking, admin, Grafana and Jenkins" /></a>

<details>
<summary><b>🔭 How Llama Express works</b> &nbsp;(architecture, decisions, Node.js and Go equivalents)</summary>
<br />

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#0e1538','primaryTextColor':'#ecf1ff','primaryBorderColor':'#ffb524','lineColor':'#5b7cff','secondaryColor':'#0e1538','tertiaryColor':'#070b22','clusterBkg':'#070b22','clusterBorder':'#26326e','fontFamily':'ui-monospace, monospace'}}}%%
flowchart LR
  customer([Customer<br/>React on Vercel]) --> cf[Cloudflare Tunnel]
  courier([Courier<br/>phone browser]) --> cf
  midtrans([Midtrans]) -->|signed webhook| cf
  cf --> gw[NGINX Gateway]
  subgraph k8s [Kubernetes]
    gw --> be[API x2<br/>Spring Boot, Java 25]
    be --> ora[(Oracle<br/>orders + outbox)]
    be --> redis[(Redis<br/>rate limits)]
    be <-->|events| kafka{{Kafka}}
  end
  be -.->|WebSocket STOMP| customer
  be -.->|WebSocket STOMP| courier
  github([GitHub]) --> jenkins[Jenkins<br/>test, scan, build] --> hub[(Docker Hub)] --> be
```

| Problem | Decision |
| --- | --- |
| An order is saved but its event never reaches Kafka | Transactional outbox: the order and its event are written in one transaction; a scheduled publisher forwards events. |
| Two pods, but WebSocket subscribers live in one pod's memory | Each pod consumes status and location events with its own Kafka consumer group and forwards them to its own browsers. |
| Scheduled jobs would run twice after scaling out | ShedLock on the outbox publisher, dispatch sweeper and housekeeping. |
| A bad release reaches the cluster | Jenkins records the running images, rolls out the new SHA, smoke-tests it and restores the previous images on failure. |

> **Coming from Node.js?** Spring Boot controllers map to Express routes, Spring's `@Transactional` replaces manual `BEGIN/COMMIT` with `pg` or Sequelize transactions, and STOMP over WebSocket is the Spring take on Socket.IO rooms. In Go, the same service would be Gin handlers with `segmentio/kafka-go` and a hand-written outbox loop.

</details>

<br />

<a href="https://github.com/farhantaufikrahman/CosFit-FinPrjctHacktiv8"><img src="assets/card-cosfit.svg" width="100%" alt="Mission 03, CosFit: AI virtual cosplay try-on with Next.js, MongoDB and Gemini" /></a>

<p align="center">
  <a href="https://cosfitai.vzkyrielight.xyz"><img src="https://img.shields.io/badge/%E2%96%B6_Live_demo-ff7ab8?style=for-the-badge&labelColor=070b22" alt="CosFit live demo" /></a>
  <a href="https://github.com/farhantaufikrahman/CosFit-FinPrjctHacktiv8"><img src="https://img.shields.io/badge/Repository-070b22?style=for-the-badge&logo=github&logoColor=white" alt="CosFit repository" /></a>
</p>

<a href="https://github.com/farhantaufikrahman/TripSync-Planner"><img src="assets/card-tripsync.svg" width="100%" alt="Mission 04, TripSync: collaborative travel planner with Express, PostgreSQL and Socket.IO" /></a>

<p align="center">
  <a href="https://tripsync.vzkyrielight.xyz"><img src="https://img.shields.io/badge/%E2%96%B6_Live_demo-5ec8ff?style=for-the-badge&labelColor=070b22" alt="TripSync live demo" /></a>
  <a href="https://github.com/farhantaufikrahman/TripSync-Planner"><img src="https://img.shields.io/badge/Repository-070b22?style=for-the-badge&logo=github&logoColor=white" alt="TripSync repository" /></a>
</p>

<a href="https://github.com/farhantaufikrahman/Kyriegram-Mobile-InstaClone-"><img src="assets/card-kyriegram.svg" width="100%" alt="Mission 05, Kyriegram: Instagram-style mobile app with React Native, Expo and GraphQL" /></a>

<p align="center">
  <a href="https://expo.dev/accounts/farhanrahman/projects/client-1/updates/bb99d561-68a9-490a-8cb6-85a1a1843fb5"><img src="https://img.shields.io/badge/Open_in_Expo-b892ff?style=for-the-badge&logo=expo&logoColor=white&labelColor=070b22" alt="Open Kyriegram in Expo" /></a>
  <a href="https://github.com/farhantaufikrahman/Kyriegram-Mobile-InstaClone-"><img src="https://img.shields.io/badge/Repository-070b22?style=for-the-badge&logo=github&logoColor=white" alt="Kyriegram repository" /></a>
</p>

## 🧰 Stack

<img src="assets/stack.svg" width="100%" alt="Tech stack. Languages: Java, Go, TypeScript, JavaScript, Python, Bash. Frameworks: Spring Boot, Gin, gRPC, Node.js, Express, GraphQL, Socket.IO, WebSocket. Frontend: React, Next.js, React Native, Expo, TanStack, Redux, Tailwind, Vite. Data and events: Oracle, PostgreSQL, MongoDB, Redis, Kafka, NATS, Sequelize. Quality: JUnit, Jest, Vitest, Testing Library, MSW, Postman. CI/CD: Jenkins, GitHub Actions, Docker, SonarQube, Flyway. Orchestration: Kubernetes, Helm, Kustomize, Gateway API, NGINX, Linux. Cloud and ops: AWS, Cloudflare, Prometheus, Grafana." />

## 📡 Telemetry

<img src="https://raw.githubusercontent.com/farhantaufikrahman/farhantaufikrahman/output/telemetry.svg" width="100%" alt="GitHub telemetry: contributions, streaks, commits, repositories, pull requests, stars and top languages, refreshed twice a day" />

## ✨ Flight path

<img src="assets/journey.svg" width="100%" alt="Flight path: B.Eng. Electrical Engineering at UPI (2020-2024), IT Technical OJT at AirNav Indonesia (2023), NOC O&M for SATRIA-1 at Pasifik Satelit Nusantara (2024-2026), Hacktiv8 Full-Stack JavaScript Immersive (2026), AWS re/Start (2026-now)" />

## ☄️ Comet log

<img src="https://raw.githubusercontent.com/farhantaufikrahman/farhantaufikrahman/output/night-snake.svg" width="100%" alt="My contribution graph as a night sky, with a comet eating the brightest stars" />

<p align="center">
  <a href="https://portofolio.vzkyrielight.xyz"><img src="assets/footer.svg" width="100%" alt="Clear skies, and thanks for stopping by. portofolio.vzkyrielight.xyz" /></a>
</p>

<details>
<summary><sub>🔧 How this profile is built</sub></summary>
<br />

- Every image is a hand-built, self-contained SVG in the same pixel night-sky style as [my portfolio](https://github.com/farhantaufikrahman/main-portofolio): the Jersey 10 font and the pixel sprites are inlined, because GitHub's image proxy blocks external requests from inside SVGs. Animations are plain CSS and SMIL, and they switch off under `prefers-reduced-motion`.
- `scripts/build_svgs.py` draws the banner, the mission cards, the stack, the flight path and the footer.
- `.github/workflows/sky.yml` runs twice a day: it generates the contribution snake with [Platane/snk](https://github.com/Platane/snk), re-skins it as a comet (`scripts/skin_snake.py`) and draws the telemetry card from the GitHub GraphQL API (`scripts/telemetry.py`). No third-party stats server, so nothing gets rate-limited.

</details>
