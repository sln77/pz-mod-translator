# Proje Zomboid Mod Çevirmeni

Yerel bir `llama.cpp` sunucusu (`llama-server`) ile çalışan ve **TranslateGemma** tarafından desteklenen, **Project Zomboid (Build 42.15+)** modlarını yerelleştirmek için kullanılan bir komut satırı aracı.

Bu, Steam Workshop veya yerel mod klasörlerinde `Translate/EN/*.json` dosyalarını tarar, çeviri hacmini (satır ve karakter sayısı) tahmin eder, eksik veya güncellenmiş metinleri çevirir ve oluşturulan her çeviriyi yerel olarak yansıtır, böylece bağımsız çeviri modlarını kolayca paketleyebilir veya Steam güncellemeleri sonrasında dosyaları geri yükleyebilirsiniz.

---

## Özellikler

- **42.15+ JSON Desteği:** Project Zomboid B42.15+ tarafından kullanılan modern `.json` çeviri formatıyla çalışır (eski `.txt` formatındaki modlar, tarama sırasında güvenli bir şekilde atlanır).
- **Zengin Terminal Arayüzü:** Temiz, renkli tablolar, durum simgeleri ve `rich` ile elde edilen, geçen/kalan süreye göre canlı ilerleme çubukları.
- **Çok dilli komut satırı arayüzü (`i18n`):** Varsayılan olarak İngilizce'ye ayarlanır ve etkileşimli başlatma sırasında `cli_locales/*.json`'dan arayüz dilini seçmek için kullanıcıyı yönlendirir.
- **3 Çalışma Modu:**
  - **Mod 1:** Belirli bir modu (veya onun `Translate` / `EN` klasörünü) çevirin.
  - **Mod 2:** Tüm Workshop dizinini tarayın, her mod için çeviri durumunu ve karakter hacmini inceleyin ve modları sayılarla (`1,3,5`), aralıklarla (`1-4`) veya `tüm` olarak seçin.
  - **Mod 3:** Kaydedilmiş ilerlemeyi yönet — mod güncellemelerini algıla, yalnızca yeni/değişen dizeyi çevir, baştan yaz, bir yedeğinden geri yükle veya oluşturulan dosyaları temiz bir şekilde sil.
- **Güncelleme Tespiti ve İlerleme Takibi:** Kaynak İngilizce metinlerin her anahtar için SHA-1 hash'lerini `pz_translator_state.json` dosyasında saklar. Eğer Steam Workshop'ta bir güncelleme yapılırsa, yalnızca yeni eklenen veya değiştirilen İngilizce anahtarlar çeviri için sıraya alınır.
- **Yerel Yansıma (`pz_translator_mods/`):** Çevrilmiş her dosyanın bir kopyasını kaydeder ve ilgili dizin yapısını korur (bu, bağımsız çeviri odaklı modlar oluşturmayı kolaylaştırır).
- **Güvenli ve Hata Tolerant:**
  - Var olan yazar çevirileri, `0` bekleyen anahtar ile birlikteyse, hiçbir şekilde değiştirilmez, üzerine yazılmaz veya izlenmez.
  - UTF-8 baş bayrağını, elle düzenlenmiş mod JSON dosyalarındaki son virgülleri ve `$schema` ve boş dizeleri işler.
  - Otomatik olarak ilerlemeyi periyodik olarak kaydeder (`save_every`) ve `Ctrl+C` tuşlarına basıldığında kaydeder.

---

## Gereksinimler

- **Python 3.9+**
- **llama.cpp** (`llama-server`) adlı, yapılandırılmış host/port üzerinde çalışan **TranslateGemma** GGUF modelini çalıştırır (varsayılan: `http://127.0.0.1:8734`).
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
    "save_every": 20
}
```

| Anahtar | Açıklama |
| --- | --- |
| `llamacpp_host` | `llama-server` uygulamanızın ana makine adresi |
| `llamacpp_port` | Çalışan `llama-server`'ınızın bağlantı noktası |
| `mods_path` | Varsayılan kök dizini, Mod 2'de (örneğin, Steam Workshop'taki `108600` klasörü) taranmıştır. |
| `default_kaynak_dil` | Kaynak çeviri klasörünün adı (varsayılan: `EN`) |
| `default_target_lang` | Varsayılan hedef dil kodu (örneğin, `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Varsayılan arayüz dil kodu, `cli_locales/` dizininden |
| `mirror_dir` | Yerel klasör, oluşturulan çevirilerin tam yolunu içeren kopyalarının saklandığı yer |
| `state_file` | JSON dosyası, çeviri geçmişini ve kaynak dize hash'lerini saklar |
| `save_every` | İlerlemenin diske kaydedilmesi ve her N çevrilmiş anahtarın kopyalanması |

---

## Kullanım

### Etkileşimli Mod

Öncelikle `llama-server`'ı başlatın, ardından şu komutu çalıştırın:

```bash
python pz_translate.py
```

1. **Arayüz Dili Seçimi:** `cli_locales/` içindeki mevcut dillerden birini seçin (varsayılan: `en`).
2. **Mod Seçimi:**
   - `1` — Belirli bir mod yolunu çevir.
   - `2` — `mods_path` içindeki tüm modları tarayın, string/karakter sayısını gösteren tabloyu görüntüleyin ve mod numaralarını girin (örneğin, `1,3,5`, `1-4` veya `tüm`).
   - `3` — Kaydedilmiş ilerlemeyi yönet (değişen/yeni anahtarları güncelle, baştan çeviri yap, `pz_translator_mods/`'den geri yükle veya çevirileri sil).
   - `4` — Arayüz dilini değiştir.
   - `0` — Çıkış.

### Komut Satırı Argümanları

CLI bayraklarını kullanarak etkileşimli menüyü atlayabilirsiniz (CLI argümanları, `config.json` dosyasını geçersiz kılar):

| Bayrak | Açıklama |
| --- | --- |
| `--config <yol>` | ...config.json... dosyasının yolu |
| `--mode {1, 2, 3}` | `1` = tek mod, `2` = dizin tarama, `3` = kaydedilmiş ilerlemeyi yönet |
| `--path <yol>` | Mod klasörüne giden yol (Mod 1) veya modların kök klasörüne giden yol (Mod 2) |
| `--lang <code>` | Hedef dil, PZ klasör kodu olarak (`RU`, `CN`, `PTBR`) veya ISO kodu olarak (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Kaynak dil klasörünü geçersiz kıl (varsayılan: `EN`) |
| `--host <host>` | `llamacpp_host` değerini geçersiz kıl |
| `--port <port>` | `llamacpp_port` değerini geçersiz kıl |
| `--ui-lang <code>` | Arayüz dil kodu (örneğin, `en`, `ru`) |
| `--force` | Mevcut çevirileri geçersiz kıl |

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
```

---

## Nasıl Çalışır

1. **Mod Keşfi:** `Translate/<SOURCE_LANG>` dizinlerini, `.json` dosyalarını içeren ve `mod.info` ve Workshop klasör yapılarından (`mods/<ModName>/<Version>`) mod adlarını çıkaran, yinelemeli bir şekilde arama yapar.
2. **Fark ve Hacim Tahmini:** `EN/*.json` içindeki anahtarları mevcut hedef dosyalarla (`<TARGET_LANG>/*.json`) ve `pz_translator_state.json`'deki depolanmış SHA-1 hash'leriyle karşılaştırır. Sadece eksik anahtarlar veya İngilizce kaynak metni son çeviriden bu yana değişen anahtarlar sıraya alınır.
3. **LLM Çevirisi:** Her string'i, `http://<host>:<port>/completion` adresine, TranslateGemma sohbet turu formatlaması kullanarak gönderir.
4. **Çift Çıktı:** Her `save_every` anahtar (ve tamamlanma veya `Ctrl+C` durumunda), geçerli UTF-8 JSON'ı aşağıdaki konumlara yazar:
   - Hedef mod dizini: `...\Translate\<LANG>\<file>.json`
   - Yerel yansıtma klasörü: `pz_translator_mods\<tam_yol_sürücü_harfi_olmadan>\Translate\<DİL>\<dosya>.json`

---

## Notlar & Sınırlamalar

- **Desteklenen Format:** Sadece Project Zomboid **42.15+** sürümünün `.json` localization dosyaları işlenir. Eski `.txt` çeviri dosyaları, B42.15+ tarafından artık yüklenmediği için göz ardı edilir.
- **Çok Oyunculu (`DoLuaChecksum`):** `Translate` klasörleri, `media/lua/shared/` içinde bulunduğundan, çeviri dosyalarını doğrudan Steam Workshop klasörlerine eklemek, `DoLuaChecksum=true` olan çok oyunculu sunucularda checksum uyuşmazlıklarına neden olabilir. Kamu çok oyunculu sunucular için, `pz_translator_mods/`'den yansıtılmış dosyaları ayrı bir çeviri moduna paketleyin veya `DoLuaChecksum=false` ile tek oyunculu / sunucularda oynayın.
```
