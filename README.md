# ExamWatch

ExamWatch 是一个基于人工智能和人脸识别技术的智能考试监控系统，旨在通过自动化监控和数据分析，提升考试过程的公平性和效率。

## 功能特性

- **人脸识别**：通过人脸识别技术确保考生身份，避免替考等作弊行为。
- **实时监控**：通过视频监控技术，实时检测考场异常行为，确保考试的公正性。
- **数据可视化**：生成详细的考试数据报告，帮助管理者分析学生表现及考试趋势。
- **防作弊机制**：通过多维度监控，智能识别并警告潜在作弊行为。

## 系统架构

该系统采用前后端分离架构，前端使用 Vue.js 开发，后端使用 Java 和 Spring Boot 提供支持，数据库使用 MySQL 来存储用户信息、考试数据和人脸数据。

## 技术栈

- **前端**：Vue.js, Axios
- **后端**：Java, Spring Boot, JPA, MySQL
- **AI 处理**：人脸识别技术 (OpenCV, Dlib)，自然语言处理 (NLP) 技术
- **其他**：Docker, Redis, WebSocket（实时通信）

## 安装与运行

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ExamWatch.git
cd ExamWatch
