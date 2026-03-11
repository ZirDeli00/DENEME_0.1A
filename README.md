# Hakan ÇELİK Yapay Zeka Sohbet

Bu proje artık statik HTML yerine **Python API arka planı + dinamik sohbet motoru** ile çalışır.

## Mimari
- `Hakan_CELIK_Chat.html`: Sohbet arayüzü (frontend)
- `launcher.py`: Yerel API sunucusu + yapay zeka mantığı + bellek + RAG-lite
- `knowledge_base/*.txt`: Bilgi tabanı dosyaları (RAG için)
- `build_exe.bat`: Windows EXE paketleme

## Geliştirilen AI Özellikleri
- Statik if/else yerine **olasılıksal niyet skorlama**
- **Short-term memory**: Son 5-10 mesaj bağlamını saklayıp yanıta dahil etme
- **Chain-of-thought tarzı** iç akıl yürütme özeti (niyet/güven)
- Python backend üzerinde merkezi karar mekanizması
- Basit **RAG-lite**: `knowledge_base` içinde arama yapıp kaynaklı cevap üretme
- Kalıcı oturum belleği: isim/hedef/tercih vb. bilgileri `.hakan_memory.json` içinde tutma

## Çalıştırma
1. Sunucuyu başlatın:
   ```bash
   python launcher.py
   ```
2. Tarayıcıdan açın:
   - `http://127.0.0.1:8000`

## Windows EXE
- `build_exe.bat` API sunucusunu ve gerekli dosyaları tek EXE olarak paketler.
