# Hakan ÇELİK Yapay Zeka Sohbet

Bu proje artık statik cevaplar yerine **gerçek LLM (Ollama + llama3)** ile konuşur.

## Mimari
- `Hakan_CELIK_Chat.html`: Sohbet arayüzü (frontend)
- `launcher.py`: Yerel API sunucusu + niyet analizi + bellek + Ollama istemcisi
- `knowledge_base/*.txt`: Bilgi tabanı dosyaları (RAG-lite)
- `build_exe.bat`: Windows EXE paketleme

## Geliştirilen AI Özellikleri
- Backend'de Ollama entegrasyonu (`http://localhost:11434/api/generate`)
- Varsayılan model: `llama3`
- Kısa süreli bağlam: son 5-10 mesaj ile konuşma bütünlüğü
- Kalıcı bellek: isim/hedef/tercih bilgileri
- RAG-lite: `knowledge_base` içinde ilgili metinleri bulup prompt'a ekleme
- Niyet analizi backend içinde çalışır fakat kullanıcıya debug metni gösterilmez

## Çalıştırma
1. Ollama'yı başlatın ve modeli çekin:
   ```bash
   ollama run llama3
   ```
2. API sunucusunu başlatın:
   ```bash
   python launcher.py
   ```
3. Tarayıcıdan açın:
   - `http://127.0.0.1:8000`

## Windows EXE
- `build_exe.bat` API sunucusunu ve gerekli dosyaları tek EXE olarak paketler.
