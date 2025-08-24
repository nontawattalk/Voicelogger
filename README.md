# Voicelogger - Enhanced Voice Transcription with Archive System

## Overview
**Voicelogger** เป็นแอปพลิเคชัน transcription ที่พัฒนาต่อยอดจาก Vibe โดยเพิ่มระบบการจัดการและเก็บถาวรไฟล์ (Archive System) พร้อมคุณสมบัติเพิ่มเติมสำหรับการใช้งานระยะยาว

## ✨ Core Features (สืบทอดจาก Vibe)
- 🎙️ **Offline Transcription** - ใช้ OpenAI Whisper แบบ local
- 🌍 **Multi-language Support** - รองรับหลายภาษา
- 🔒 **Ultimate Privacy** - ข้อมูลไม่ออกจากเครื่อง
- 📁 **Batch Processing** - ประมวลผลหลายไฟล์พร้อมกัน
- 📝 **Multiple Export Formats** - SRT, VTT, TXT, HTML, PDF, JSON, DOCX
- 🎨 **User-friendly Interface** - ใช้งานง่าย
- 💻 **GPU Optimization** - รองรับ NVIDIA/AMD/Intel
- 🎤 **Real-time Recording** - บันทึกเสียงจากไมโครโฟนและระบบ
- 👥 **Speaker Diarization** - แยกผู้พูด
- 🧠 **AI Summarization** - สรุปเนื้อหาด้วย AI

## 🗂️ Enhanced Features - Archive System

### 1. **Smart Archive Management**
- **Auto-archiving** - เก็บถาวรไฟล์อัตโนมัติตามเงื่อนไข
- **Custom Archive Rules** - กำหนดกฎการเก็บถาวรเอง
- **Compression Options** - บีบอัดไฟล์เพื่อประหยัดพื้นที่
- **Archive Encryption** - เข้ารหัสไฟล์ที่เก็บถาวร

### 2. **Advanced File Organization**
- **Project-based Organization** - จัดกลุ่มไฟล์ตามโปรเจ็กต์
- **Tags & Labels** - ติดป้ายกำกับและแท็ก
- **Smart Folders** - โฟลเดอร์อัตโนมัติตามเงื่อนไข
- **Version Control** - เก็บประวัติการแก้ไขไฟล์

### 3. **Search & Discovery**
- **Full-text Search** - ค้นหาในเนื้อหา transcript
- **Metadata Search** - ค้นหาจากข้อมูลเมตา
- **Advanced Filters** - กรองผลลัพธ์แบบละเอียด
- **Quick Access** - เข้าถึงไฟล์ที่ใช้บ่อยได้เร็ว

## 📊 Database & Storage Architecture

### Database Schema
```sql
-- Projects Table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    color_theme TEXT
);

-- Files Table
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    original_filename TEXT,
    archived_filename TEXT,
    file_type TEXT, -- audio/video/transcript
    file_size INTEGER,
    duration INTEGER, -- in seconds
    language TEXT,
    status TEXT, -- active/archived/deleted
    created_at DATETIME,
    archived_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Transcripts Table
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY,
    file_id INTEGER,
    content TEXT,
    format TEXT, -- srt/vtt/txt/etc
    confidence_score REAL,
    word_count INTEGER,
    created_at DATETIME,
    FOREIGN KEY (file_id) REFERENCES files (id)
);

-- Tags Table
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    color TEXT
);

-- File Tags Junction
CREATE TABLE file_tags (
    file_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (file_id, tag_id)
);

-- Archive Rules
CREATE TABLE archive_rules (
    id INTEGER PRIMARY KEY,
    name TEXT,
    condition_type TEXT, -- age/size/project/tag
    condition_value TEXT,
    action TEXT, -- move/compress/encrypt
    enabled BOOLEAN DEFAULT TRUE
);
```

### File Structure
```
~/Voicelogger/
├── active/              # ไฟล์ที่ใช้งานอยู่
│   ├── projects/
│   └── temp/
├── archive/             # ไฟล์ที่เก็บถาวร
│   ├── 2024/
│   ├── 2025/
│   └── compressed/
├── database/
│   └── voicelogger.db
└── config/
    ├── settings.json
    └── archive_rules.json
```

## 🎯 User Interface Design

### Main Dashboard
- **Project Overview Cards** - แสดงโปรเจ็กต์ทั้งหมด
- **Recent Activity** - กิจกรรมล่าสุด
- **Storage Usage** - การใช้พื้นที่จัดเก็บ
- **Quick Actions** - การดำเนินการด่วน

### Archive Manager
- **Timeline View** - มุมมองตามเวลา
- **Storage Analytics** - วิเคราะห์การใช้พื้นที่
- **Archive Rules Manager** - จัดการกฎการเก็บถาวร
- **Bulk Operations** - ดำเนินการหลายไฟล์

### Advanced Search Interface
- **Search Bar** - ค้นหาแบบ natural language
- **Filter Panels** - กรองแบบละเอียด
- **Results Preview** - ดูตัวอย่างผลลัพธ์
- **Export Options** - ส่งออกผลการค้นหา

## ⚙️ Technical Implementation

### Technology Stack
- **Frontend**: Tauri + React/TypeScript
- **Backend**: Rust (Tauri backend)
- **Database**: SQLite with FTS5 for full-text search
- **Transcription**: Whisper.cpp (Rust bindings)
- **Compression**: zstd for fast compression
- **Encryption**: AES-256 for sensitive data

### Key Components

#### Archive Service
```rust
pub struct ArchiveService {
    db: Database,
    storage: StorageManager,
    compressor: Compressor,
    encryptor: Encryptor,
}

impl ArchiveService {
    pub async fn auto_archive(&self) -> Result<()> {
        let rules = self.db.get_active_archive_rules().await?;
        for rule in rules {
            let files = self.find_files_matching_rule(&rule).await?;
            self.execute_archive_action(files, &rule.action).await?;
        }
        Ok(())
    }
}
```

#### Search Engine
```rust
pub struct SearchEngine {
    db: Database,
    index: FullTextIndex,
}

impl SearchEngine {
    pub async fn search(&self, query: &SearchQuery) -> Result<Vec<SearchResult>> {
        let mut results = Vec::new();
        
        // Full-text search in transcripts
        if !query.text.is_empty() {
            results.extend(self.search_transcripts(&query.text).await?);
        }
        
        // Metadata search
        results.extend(self.search_metadata(query).await?);
        
        // Apply filters and sorting
        self.apply_filters_and_sort(results, query).await
    }
}
```

## 📱 Mobile Integration (Future)
- **iOS/Android Apps** - แอปมือถือ
- **Cloud Sync** - ซิงค์ข้อมูลแบบเข้ารหัส
- **Voice Notes** - บันทึกเสียงด่วน
- **Offline Mode** - ใช้งานแบบออฟไลน์

## 🔐 Security Features
- **Local Encryption** - เข้ารหัสไฟล์ในเครื่อง
- **Secure Deletion** - ลบไฟล์อย่างปลอดภัย
- **Backup Verification** - ตรวจสอบความถูกต้องของ backup
- **Privacy Controls** - ควบคุมความเป็นส่วนตัว

## 🚀 Deployment & Distribution
- **Cross-platform Installer** - ติดตั้งง่ายทุกระบบ
- **Auto-update System** - อัพเดทอัตโนมัติ
- **Portable Version** - รุ่น portable ไม่ต้องติดตั้ง
- **Enterprise Edition** - รุ่นสำหรับองค์กร

## 📈 Performance Metrics
- **Transcription Speed**: 10x faster than real-time
- **Storage Efficiency**: 80% space savings with smart compression
- **Search Speed**: Sub-second search across thousands of files
- **Battery Optimization**: 40% less power consumption on mobile

## 🎨 UI/UX Highlights
- **Dark/Light Themes** - ธีมที่สวยงาม
- **Customizable Workspace** - ปรับแต่งพื้นที่ทำงาน
- **Keyboard Shortcuts** - ทางลัดคีย์บอร์ด
- **Accessibility Support** - รองรับผู้พิการ

## 🔄 Migration from Vibe
- **Import Wizard** - นำเข้าไฟล์จาก Vibe
- **Settings Migration** - ย้ายการตั้งค่า
- **Batch Processing** - ประมวลผลไฟล์เก่าเป็นชุด
- **Backward Compatibility** - รองรับไฟล์รูปแบบเดิม

---
