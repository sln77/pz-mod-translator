# Project Zomboid Mod Çevirmeni

**Project Zomboid (42.15+)** modlarını yerel bir `llama.cpp` sunucusu (`llama-server`) aracılığıyla ve **TranslateGemma** teknolojisiyle yerelleştirmek için kullanılan bir komut satırı aracı.

Steam Workshop veya yerel mod klasörlerini `Translate/EN/*.json` dosyaları için tarar, çeviri hacmini (satır ve karakter sayısı) tahmin eder, eksik veya güncellenmiş metinleri çevirir, değişkenleri ve kullanıcı arayüzü işaretlerini doğrular ve oluşturulan her çeviriyi yerel olarak yansıtır, böylece bağımsız çeviri modlarını kolayca paketleyebilir veya Steam güncellemeleri sonrasında dosyaları geri yükleyebilirsiniz.

---

## Özellikler

- **42.15+ JSON Desteği:** Project Zomboid B42.15+ tarafından kullanılan modern `.json` çeviri formatıyla çalışır (eski `.txt` formatındaki modlar, tarama sırasında güvenli bir şekilde atlanır).
- **Zengin Terminal Arayüzü:** Temiz renkli tablolar, durum simgeleri ve `rich` kütüphanesini kullanarak geçen/kalan süre ile birlikte gerçek zamanlı ilerleme çubukları.
- **Çok dilli komut satırı arayüzü (`i18n`):** Varsayılan olarak İngilizce dilini kullanır ve etkileşimli başlatma sırasında, `cli_locales/*.json` dosyasından arayüz dilini seçme isteği sunar.
- **3 Farklı Çalışma Modu:**
  - **Mod 1:** Belirli bir modun (veya `Translate` / `EN` klasörünün) çevrilmesini yapın.
  - **Mod 2:** Tüm çalışma alanınızı tarayın, her mod için çeviri durumunu ve karakter sayısını inceleyin ve modları `1,3,5` (sayılar), `1-4` (aralıklar) veya `all` (belirtilen modlar) ile seçin.
  - **Modül 3:** Kaydedilmiş ilerlemeyi yönet — mod güncellemelerini tespit et, yeni/değişen/bozuk token dizilerini çevir, sıfırdan yeniden oluştur, bir yedeğinden geri yükle, oluşturulan dosyaları temiz bir şekilde sil veya token kontrol raporunu çalıştırma.
- **Yer Tutucu ve İşaretleme Doğrulaması (`token_rules.json`):** Yapılandırılabilir düzenli ifadeler kullanarak mod yer tutucularını (`{name}`, `%1`) ve Project Zomboid RichText etiketlerini (`<LINE>`, `<RGB:...>`, `<IMAGE:...>`, vb.) çıkarır ve çeviri sonrasında tam bir eşleşme olup olmadığını doğrular. Eşleşme sağlanmazsa, farklı tohumlarla tekrar denemeye çalışır (`max_retries`). Tüm denemeler başarısız olursa, orijinal İngilizce metni korur, mod durumunu `EN/<LANG>` olarak işaretler ve detayları `pz_translator_issues.log` dosyasına kaydeder.
- **Güncelleme Tespiti ve İlerleme Takibi:** Kaynak İngilizce metinlerin her anahtar için SHA-1 hash'lerini `pz_translator_state.json` dosyasında saklar. Eğer Steam Workshop'ta bir güncelleme yapılırsa, yalnızca yeni eklenen, değiştirilen veya bozuk anahtarlar çeviri için sıraya alınır.
- **Yerel Yansıtıcı (`pz_translator_mods/`):** Çevrilmiş her dosyanın bir kopyasını kaydeder ve ilgili dosya yapısını korur (bu, bağımsız çeviri odaklı modlar oluşturmayı kolaylaştırır).
- **Güvenli ve Hata Toleranslı:**
  - Önceden var olan yazar tarafından çevrilmiş metinler (hem orijinal haliyle olan modlar hem de `pz_translator_state.json` dosyasında takip edilmeyen, bireysel yazar tarafından çevrilmiş anahtarlar) asla token kuralları tarafından analiz edilmez, değiştirilmez veya üzerine yazılmaz.
  - UTF-8 başlık karakterini, elle düzenlenmiş mod JSON dosyalarındaki sondaki virgülleri ve `$schema` ve boş dizeleri korur.
  - Otomatik olarak düzenli aralıklarla kaydedilir (`save_every`) ve `Ctrl+C` tuşuna basıldığında da kaydedilir.

---

## Gereksinimler

- **Python 3.9 veya daha yeni bir sürümü**
- **llama.cpp** (`llama-server`) adlı uygulama, yapılandırılmış sunucu/port üzerinde **TranslateGemma** GGUF modelini çalıştırıyor (varsayılan: `http://127.0.0.1:8734`).
- Python bağımlılıkları:

```bash
pip install -r requirements.txt
```

---

## Yapılandırma (`config.json`)

İlk çalıştırmada (veya dahil edilen `config.json` dosyası aracılığıyla), script aşağıdaki ayarları kullanır:

```json
{
    "llamacpp_host": "127.0.0.1",
    "llamacpp_port": 8734,
    "mods_path": "Z:\\steam\\steamapps\\workshop\\content\\108600",
    "default_source_lang": "EN",
    "default_target_lang": "RU",
    "ui_lang": "en",
    "mirror_dir": "pz_translator_mods",
    "state_file": "pz_translator_state.json",
    "token_rules_file": "token_rules.json",
    "save_every": 20
}
```

| Anahtar | Açıklama |
| --- | --- |
| `llamacpp_host` | `llama-server` uygulamanızın ana adresi |
| `llamacpp_port` | Çalışan `llama-server` uygulamanızın bağlantı noktasını belirtin. |
| `mods_path` | Varsayılan kök dizini, Mod 2 (örneğin, Steam Workshop'taki `108600` klasörü) modunda taranmıştır. |
| `default_source_lang` | Kaynak çeviri klasörünün adı (varsayılan: `EN`) |
| `default_target_lang` | Varsayılan hedef dil kodu (örneğin, `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Varsayılan arayüz dil kodu, `cli_locales/` dizininden |
| `mirror_dir` | Yerel klasör, oluşturulan çevirilerin tam yolunu içeren kopyalarının saklandığı yer. |
| `state_file` | JSON dosyası, çeviri geçmişini ve kaynak metinlerin hash değerlerini saklar. |
| `token_rules_file` | Yer tutucu/etik doğrulaması için düzenli ifadeler ve yeniden deneme ayarları içeren JSON dosyası |
| `save_every` | İlerlemenin diske kaydedilmesi ve her N çevrilmiş anahtarın bir kopyasının oluşturulması. |

### Token Doğrulama (`token_rules.json`)

`token_rules.json` dosyasında, dinamik değişkenleri ve Project Zomboid işaretleme etiketlerini korumak için kullanılan düzenler yapılandırılmıştır:

| Anahtar | Açıklama |
| --- | --- |
| `max_retries` | Kritik belirteçlerin uyuşmadığı durumlarda, farklı tohumlarla yapılan çeviri denemelerinin maksimum sayısı. |
| `retry_temperatures` | Bu sıcaklık programı, yeniden deneme girişimlerinin her birinde uygulanır (örneğin, `[0.2, 0.35, 0.5]`). |
| `issues_log` | Günlük dosyası, tüm denemelerden sonra doğrulama testi sırasında başarısız olan dize ve bunların `EN` kaynağı ve başarısız denemeleri kaydeder. |
| `check_report` | Mod 3'te gerçekleştirilen "dry-run" token inceleme raporunun çıktı dosyası |
| `rules` | Düzenli ifade kurallarının bir dizisi (`name`, `pattern`, `enabled`, `critical`, `description`) |

`"critical": true` numaralı kurallar, çeviri sırasında yeniden denemeleri tetikler ve güncellemeler sırasında yeniden çeviri için kullanılmayan anahtarları izler. Kritik olmayan kurallar (`"critical": false`), yalnızca "deneme çalıştırma" raporunda uyarı olarak belirtilir.

---

## Kullanım

### Etkileşimli Mod

Öncelikle `llama-server`'ı başlatın, ardından şu komutu çalıştırın:

```bash
python pz_translate.py
```

1. **Arayüz Dili Seçimi:** `cli_locales/` klasindeki mevcut dillerden birini seçin (varsayılan: `en`).
2. **Seçim Modu:**
   - `1` — Belirli bir mod yolunu çevirin.
   - `2` — `mods_path` içindeki tüm modları tarayın, metin/karakter sayısını gösteren tabloyu görüntüleyin ve mod numaralarını girin (örneğin, `1,3,5`, `1-4` veya `all`).
   - `3` — Kaydedilmiş ilerlemeyi yönet (yeni/değiştirilmiş/bozuk anahtarları güncelle, sıfırdan yeniden çeviri yap, `pz_translator_mods/`'den geri yükle, çevirileri sil veya token kontrol raporunu çalıştır).
   - `4` — Arayüz dilini değiştirin.
   - `0` — Çıkış

### Komut Satırı Argümanları

İnteraktif menüyü komut satırı bayrakları (CLI argümanları, `config.json` dosyasını geçersiz kılar) aracılığıyla atlayabilirsiniz.

| Bayrak | Açıklama |
| --- | --- |
| `--config <path>` | Özel bir `config.json` dosyası oluşturma yolu |
| `--rules <path>` | Özel `token_rules.json` dosyası oluşturma yolu |
| `--mode {1,2,3}` | `1` = tek mod, `2` = dizin taraması, `3` = kaydedilmiş ilerlemeyi yönet |
| `--path <path>` | Mod klasörüne giden yol (Mod 1) veya modların ana klasörüne giden yol (Mod 2) |
| `--lang <code>` | Hedef dil, PZ klasör kodu olarak (`RU`, `CN`, `PTBR`) veya ISO kodu olarak (`ru`, `zh`, `pt-BR`) belirtilmelidir. |
| `--source-lang <code>` | Kaynak dil klasörünü geçersiz kıl (varsayılan: `EN`) |
| `--host <host>` | `llamacpp_host` değerini geçersiz kıl |
| `--port <port>` | `llamacpp_port` değerini geçersiz kıl |
| `--ui-lang <code>` | Arayüz dil kodu (örneğin, `en`, `ru`) |
| `--force` | Mevcut çevirileri geçersiz kılın |
| `--check` | Tüm kaydedilmiş çeviriler üzerinde bir "dry-run" (deneme) token kontrolü gerçekleştirin ve `pz_translator_check_report.txt` adlı bir rapor oluşturun. |

#### Örnekler

```bash
# Translate a single mod to Russian
python pz_translate.py --mode 1 --path "Z:\steam\steamapps\workshop\content\108600\3268487204" --lang RU

# Force re-translation of a single mod to German
python pz_translate.py --mode 1 --path "Z:\steam\steamapps\workshop\content\108600\3268487204" --lang DE --force

# Scan all Workshop mods and pick mods interactively in Russian UI
python pz_translate.py --mode 2 --lang RU --ui-lang ru --port 8734

# Open the progress manager
python pz_translate.py --mode 3

# Run a dry-run token check on all saved translations without calling the LLM
python pz_translate.py --mode 3 --check
```

---

## Nasıl Çalışır

1. **Mod Keşfi:** `.json` dosyalarını içeren `Translate/<SOURCE_LANG>` dizinlerini, yinelemeli olarak arar ve `mod.info` ve Workshop klasör yapılarından (`mods/<ModName>/<Version>`) mod adlarını çıkarır.
2. **Fark ve Hacim Tahmini:** `EN/*.json` dosyalarındaki anahtarları, mevcut hedef dosyalarla (`<TARGET_LANG>/*.json`), `pz_translator_state.json` dosyasında saklanan SHA-1 hash değerleriyle ve `token_rules.json` dosyasından alınan önemli kurallarla karşılaştırır. Eksik anahtarlar, İngilizce kaynak metninde değişiklik olan anahtarlar ve bozuk yer tutucular/etiklerle işaretlenmiş anahtarlar çeviri için bir sıraya alınır; mevcut yazar çevirileri olduğu gibi bırakılır.
3. **LLM Çeviri ve Doğrulama:** Her tam orijinal metni, standart TranslateGemma istem formatını kullanarak `http://<host>:<port>/completion` adresine gönderir. Ardından, metindeki önemli kelimeleri orijinal metinle karşılaştırır. Eşleşme durumunda, `max_retries` kadar farklı tohumlarla tekrar denemeler yapar. Tüm denemeler başarısız olursa, İngilizce metni korur, değişiklik durumunu `EN/<LANG>` olarak işaretler ve detayları `pz_translator_issues.log` dosyasına kaydeder.
4. **Çift Çıktı:** `save_every` anahtarının her değeri (ve ayrıca tamamlandığında veya `Ctrl+C` tuşuna basıldığında), geçerli UTF-8 JSON formatında aşağıdaki konumlara kaydeder:
   - Hedef mod klasörü: `...\Translate\<LANG>\<file>.json`
   - Yerel aynalama klasörü: `pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## Notlar ve Sınırlamalar

- **Desteklenen Format:** Sadece Project Zomboid **42.15+** sürümünün `.json` formatındaki yerelleştirme dosyaları işlenir. Eski `.txt` formatındaki çeviri dosyaları, 42.15+ sürümünün artık bunları yüklemediği için göz ardı edilir.
- **Çok Oyunculu (`DoLuaChecksum`):** `Translate` klasörleri, `media/lua/shared/` içinde bulunduğundan, çeviri dosyalarını doğrudan Steam Workshop klasörlerine eklemek, `DoLuaChecksum=true` olan çok oyunculu sunucularda checksum uyumsuzluklarına neden olabilir. Kamuya açık çok oyunculu sunucular için, `pz_translator_mods/` klasörlerinden yansıtılmış dosyaları ayrı bir çeviri moduna paketleyebilir veya `DoLuaChecksum=false` ile tek oyunculu / sunucularda oynayabilirsiniz.
