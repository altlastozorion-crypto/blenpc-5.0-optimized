# MF v5.1 Mühendislik Dönüşüm Planı (Blender 5.0.1)

Bu doküman, mevcut `blenpc` projesinin profesyonel bir mimari varlık yönetim ve üretim sistemine dönüşüm yol haritasını tanımlar.

## 1. Vizyon ve Mimari Standartlar
Proje, basit bir mesh üreticiden ziyade, deterministik matematiksel kurallara dayalı, JSON komut sistemiyle çalışan bir **Mimari Motor** haline getirilecektir.

### Temel Prensipler
- **Determinizm:** Hash-tabanlı RNG zinciri ile her seed her zaman aynı sonucu verir.
- **Mühendislik Doğruluğu:** Euler manifold kontrolleri ve Golden Ratio (Altın Oran) tabanlı alan bölünmeleri.
- **Modülerlik:** Her şey bir "Atom" veya "Asset"tir; slot sistemiyle birbirine bağlanır.
- **CLI-First:** Doğrudan Python çağrısı yerine `input.json` -> `output.json` akışı.

## 2. Uygulama Adımları (Tamamlandı ✅)

| Adım | Modül | Durum |
| :--- | :--- | :--- |
| 1 | `version_check.py` | ✅ Doğrulandı |
| 2 | `config.py` | ✅ Tanımlandı |
| 3 | `_registry/` | ✅ Oluşturuldu |
| 4 | `engine/slot_engine.py` | ✅ Geliştirildi |
| 5 | `atoms/wall.py` | ✅ Üretildi |
| 6 | `run_command.py` | ✅ CLI Hazır |
| 7 | `tests/` | ✅ Testler Geçti |

## 3. Teknik Detaylar
- **Koordinat Sistemi:** Godot uyumlu Y-up sistemi.
- **Izgara (Grid):** Standart `0.25m` modüler ızgara.
- **Topoloji:** Euler Formülü ($V - E + F = 2$) ile manifold mesh garantisi.
- **RNG:** `hashlib.sha256` tabanlı bağımsız alt-sistem seed zinciri.

---
*Bu plan dinamik olarak güncellenecektir.*
