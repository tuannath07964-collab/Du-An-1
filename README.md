# 🐉 An Yên — Linh thú dẫn lối bữa lành

> **Concept website đặt bàn nhà hàng** với trải nghiệm immersive: màn hình loading 3D dragon, mô hình nhà hàng tương tác, và dashboard quản lý nội bộ — tất cả trong một file HTML duy nhất, không cần backend.

---

## 📋 Mục lục

1. [Tổng quan](#tổng-quan)
2. [Cấu trúc dự án](#cấu-trúc-dự-án)
3. [Màn hình & luồng người dùng](#màn-hình--luồng-người-dùng)
4. [Kỹ thuật & thư viện](#kỹ-thuật--thư-viện)
5. [3D Assets](#3d-assets)
6. [Màu sắc & typography](#màu-sắc--typography)
7. [Chạy dự án](#chạy-dự-án)
8. [Lịch sử phiên bản](#lịch-sử-phiên-bản)

---

## Tổng quan

**An Yên** là một concept nhà hàng fine-dining Việt Nam với mascot linh vật là rồng thủ hộ *(Guardian Dragon)*. Website tích hợp:

| Tính năng | Mô tả |
|-----------|-------|
| 🐉 **KV Intro Loader** | Màn hình loading canvas 2D: tinh thể bay, vòng enso mực tàu, cổng năng lượng → rồng xuất hiện |
| 🏠 **Hero Section** | Mascot rồng 3D tương tác (tilt theo con trỏ), nội dung giới thiệu |
| 🏛️ **Space Section** | Mô hình nhà hàng 3D dạng cutaway (diorama isometric) xem được 360° |
| 📅 **Booking Section** | Form đặt bàn: chọn ngày, giờ, số khách, số điện thoại |
| 📊 **Management Dashboard** | Dashboard nội bộ: lịch đặt hôm nay, sơ đồ bàn, danh sách khách |

---

## Cấu trúc dự án

```
AnYen-Reservation/
│
├── index.html                        ← Entry point duy nhất (3.2 MB, self-contained)
│
├── src/                              ← Source code tách biệt (phát triển tương lai)
│   ├── css/                          ← Stylesheet
│   ├── js/                           ← JavaScript modules
│   └── components/                   ← UI components
│
├── assets/                           ← Tài nguyên tĩnh
│   ├── images/
│   │   └── restaurant-cube-render.png   ← Render preview mô hình nhà hàng (1200×1200px)
│   ├── audio/                        ← (dự phòng: âm thanh)
│   ├── models/
│   │   ├── guardian-dragon-rigged.glb   ← Rồng đã rig + animation (2.0 MB) ← ĐANG DÙNG
│   │   └── restaurant-cube.glb          ← Mô hình nhà hàng cutaway (332 KB) ← ĐANG DÙNG
│   ├── fonts/                        ← (dự phòng: font local)
│   └── textures/                     ← (dự phòng: texture maps)
│
├── 3d-source/                        ← Nguồn file 3D gốc
│   ├── blender/
│   │   ├── guardian-dragon-animated.blend   ← File Blender rồng có animation (9.8 MB)
│   │   ├── restaurant-cube.blend            ← File Blender nhà hàng (175 KB)
│   │   └── restaurant-cube.blend1           ← Blender auto-backup
│   └── scripts/
│       └── create_restaurant_model.py       ← Script tạo mô hình nhà hàng từ Blender Python API
│
├── tools/                            ← Công cụ hỗ trợ phát triển
│
├── archive/                          ← Lưu trữ các phiên bản cũ
│   ├── html-versions/                ← Checkpoint HTML theo từng tính năng
│   │   ├── index.before-dragon.html
│   │   ├── index.before-blackhole.html
│   │   ├── index.before-vortex-fix.html
│   │   ├── index.before-head-fix.html
│   │   ├── index.before-arrival.html
│   │   ├── index.before-skin-animation.html
│   │   ├── index.before-final-motion.html
│   │   ├── index.before-loader-pacing.html
│   │   ├── index.before-liquid-current.html
│   │   └── index.before-liquid-wave.html
│   └── old-models/
│       └── guardian-dragon.glb       ← Phiên bản rồng chưa rig (10 MB, lưu trữ)
│
├── README.md
└── .gitignore
```

---

## Màn hình & luồng người dùng

### 🐉 KV Intro Loader (`#loader`)
Màn hình loading toàn trang, thuần Canvas 2D — **không dùng WebGL hay Three.js**:

```
[Tinh thể bay lơ lửng]
        ↓
[Vòng enso mực tàu (ink-brush ring) vẽ ra]
        ↓
[Cổng năng lượng mở ra → hiệu ứng blackhole / accretion disk]
        ↓
[Dragon xuất hiện: rồng nuốt viên ngọc (pearl-feed → pearl-bitten)]
        ↓
[Dragon roar → trang chính reveal]
```

**Các giai đoạn loader:**
| Class state | Hiệu ứng |
|-------------|----------|
| `loader.query` | Truy vấn DOM |
| `loader.pearl-form` | Viên ngọc hình thành |
| `loader.pearl-near-mouth` | Ngọc tiến về miệng rồng |
| `loader.pearl-bitten` | Rồng cắn ngọc |
| `loader.suction` | Hiệu ứng hút blackhole |
| `loader.hole-collapse` | Blackhole sụp đổ |
| `loader.dragon-sequence` | Rồng xuất hiện toàn thân |
| `loader.done` | Loader ẩn, trang hiện ra |

**Kỹ thuật canvas:**
- Quaternion math tự viết (`qmul`, `qslerp`, `qaxis`, `qmat`) để xoay tinh thể 3D trong 2D canvas
- Tinh thể 5 mặt (elongated bipyramid) với z-sorting và normal shading
- Blackhole accretion disk bằng CSS conic-gradient + animation
- Random seeded bằng thuật toán Mulberry32

---

### 🏠 Hero Section (`#home`)
- **Mascot rồng 3D** dùng `<model-viewer>` với animation `AnYen_Guardian_Idle`
- **Parallax tilt**: rồng nghiêng theo con trỏ chuột (CSS custom properties `--tilt-x/y`, `--shift-x/y`)
- **Nội dung:** "Linh long. Mở lối bữa lành." — CTA đặt bàn

**Nav links:**
- Linh thú · Không gian 3D · Đặt bàn · Quản lý

---

### 🏛️ Space Section (`#space`) — `02 / KHÔNG GIAN & VẬN HÀNH`
- **Mô hình nhà hàng 3D** (`restaurant-cube.glb`) dạng cutaway isometric
- Nhà hàng được xây từ Blender Python API: 4 bàn tròn, ghế, đèn pendant, khu vực bar, cây cảnh
- Người dùng xoay/xem 360° qua `<model-viewer>`
- Luồng hiển thị: *Khách chọn ngày giờ → nhân viên xem trạng thái bàn → quản lý theo dõi hóa đơn*

---

### 📅 Booking Section (`#booking`) — `03 / BẮT ĐẦU CUỘC HẸN`
Form đặt bàn với các trường:

| Trường | Loại | Giá trị |
|--------|------|---------|
| Chọn ngày | `date` input | — |
| Giờ đến | `select` | 18:00 / 18:30 / 19:00 / 19:30 / 20:00 |
| Số khách | `select` | 2 – 6 khách |
| Số điện thoại | `tel` input | — |

---

### 📊 Management Dashboard (`#management`) — `DÀNH CHO ĐỘI NGŨ AN YÊN`
Dashboard nội bộ mô phỏng:

| Widget | Dữ liệu |
|--------|---------|
| Lượt đặt hôm nay | 244 |
| Chờ xác nhận | hiển thị số lượng |
| Bàn đang phục vụ | 08 / 16 |
| Công suất | 50% |
| Khách dự kiến | 56 (trong 3 khung giờ) |
| Danh sách khách | Minh Anh · Gia Hân · Quốc Bảo + trạng thái |
| Sơ đồ bàn | Tầng trệt · 16 bàn (Trống / Đang dùng / Đã đặt) |

---

## Kỹ thuật & thư viện

### Thư viện ngoài
| Thư viện | Phiên bản | Dùng cho |
|----------|-----------|----------|
| [GSAP](https://gsap.com/) | 3.12.5 | Animation timeline, easing |
| [Google Model Viewer](https://modelviewer.dev/) | 4.4.0 | Render GLB 3D trong trình duyệt |
| Google Fonts | — | Permanent Marker, Ma Shan Zheng |

### Kỹ thuật tự viết (không framework)
| Module | Mô tả |
|--------|-------|
| **KVCore** | Canvas 2D engine: tinh thể 3D, quaternion rotation, z-sort, pixel painting |
| **Mulberry32 RNG** | Seeded random number generator |
| **Quaternion math** | `qmul`, `qslerp`, `qaxis`, `qmat`, `qfromto` — xoay 3D thuần JS |
| **Scroll snap** | CSS `scroll-snap-type: y proximity` — điều hướng section mượt |
| **Parallax tilt** | `pointermove` → CSS vars → 3D transform trên mascot |
| **playRoar** | Web Audio API synthesize tiếng rồng gầm (oscillator-based) |
| **heroReveal** | GSAP timeline reveal toàn bộ hero sau loader |

### Rendering pipeline
```
index.html load
    └── KVCore (Canvas 2D) chạy intro animation
        └── dragonMascot (<model-viewer>) preload GLB base64
            └── loader.done → heroReveal() → trang chính
                └── restaurantModel (<model-viewer>) lazy load
```

> **Lưu ý:** Cả hai GLB (rồng + nhà hàng) được **nhúng thẳng vào HTML dưới dạng base64** → không cần server, chỉ cần mở file. Đây là lý do file `index.html` nặng ~3.2 MB.

---

## 3D Assets

### Guardian Dragon (`guardian-dragon-rigged.glb`)
- **Tool:** Blender (file: `guardian-dragon-animated.blend`)
- **Animation:** `AnYen_Guardian_Idle` — rồng thở/đứng im
- **Dùng trong:** Hero section mascot
- Phiên bản cũ (chưa rig): `archive/old-models/guardian-dragon.glb`

### Restaurant Cube (`restaurant-cube.glb`)
- **Tool:** Blender Python API (`create_restaurant_model.py`)
- **Loại:** Cutaway isometric diorama — nhà hàng mặt cắt lớp
- **Camera:** Orthographic isometric, góc nhìn `(9.2, -11.5, 9.4)`
- **Ánh sáng:** 3 đèn Area (Key warm softbox / Fill mint rim / Back amber)
- **Nội thất:** 4 bàn tròn, ghế 2 phía, đèn pendant, quầy bar, khu vực cây, cửa vào

**Materials palette Blender:**
| Tên | Màu | Metallic | Roughness |
|-----|-----|----------|-----------|
| Charcoal \| lacquer | `#0B0F0C` | 0.18 | 0.28 |
| Deep green \| walls | `#1E3026` | 0.05 | 0.70 |
| Mint \| edge light | `#2EF29E` | 0.12 | 0.30 |
| Warm ivory \| stone | `#E8C98F` | 0.00 | 0.48 |
| Amber \| wood | `#8C4A1E` | 0.00 | 0.62 |
| Oxblood \| accent | `#610B09` | 0.05 | 0.42 |
| Brushed bronze | `#523820` | 0.72 | 0.28 |

**Script tạo model** (`create_restaurant_model.py`):
```bash
# Chạy từ Blender Scripting workspace
# Output: restaurant-cube.blend + restaurant-cube.glb + restaurant-cube-render.png
```

---

## Màu sắc & typography

### CSS Design Tokens
```css
:root {
  --bg:     #171717;   /* Nền tối chính */
  --panel:  #222722;   /* Panel / card */
  --mint:   #88f9c0;   /* Mint xanh — accent chính */
  --cream:  #f4d9a0;   /* Kem vàng — text phụ */
  --orange: #c8792c;   /* Cam đất — highlight */
  --paper:  #f4efe5;   /* Trắng ngà — text chính */
  --muted:  #a9afa7;   /* Xám mờ — text phụ */
  --line:   #ffffff20; /* Viền mờ */
}
```

### Fonts
| Font | Nguồn | Dùng cho |
|------|-------|----------|
| Inter / Segoe UI | System | Body text |
| Georgia | System | Brand name, em italic |
| Permanent Marker | Google Fonts | Accent display |
| Ma Shan Zheng | Google Fonts | Chữ Hán/thư pháp |

---

## Chạy dự án

Vì toàn bộ assets (GLB, fonts) đã được **embed dưới dạng base64** trong HTML:

```bash
# Cách 1: Mở trực tiếp
# Double-click vào index.html trong trình duyệt

# Cách 2: Local server (khuyến nghị để tránh CORS)
python -m http.server 8080
# Mở: http://localhost:8080

# Cách 3: VS Code Live Server
# Cài extension "Live Server" → Click "Go Live"
```

> **Trình duyệt được hỗ trợ:** Chrome 90+, Edge 90+, Firefox 85+, Safari 15+  
> (Cần hỗ trợ `<model-viewer>`, CSS `scroll-snap`, Canvas 2D API)

---

## Lịch sử phiên bản

Các checkpoint được lưu tại `archive/html-versions/`:

| File | Mô tả |
|------|-------|
| `index.before-dragon.html` | Trước khi thêm rồng 3D |
| `index.before-blackhole.html` | Trước hiệu ứng blackhole loader |
| `index.before-vortex-fix.html` | Trước khi fix vortex animation |
| `index.before-head-fix.html` | Trước khi fix đầu rồng |
| `index.before-arrival.html` | Trước animation rồng xuất hiện |
| `index.before-skin-animation.html` | Trước animation skin/vảy rồng |
| `index.before-final-motion.html` | Trước motion cuối cùng |
| `index.before-loader-pacing.html` | Trước điều chỉnh tốc độ loader |
| `index.before-liquid-current.html` | Trước hiệu ứng dòng chảy |
| `index.before-liquid-wave.html` | Trước hiệu ứng sóng lỏng |

**Phiên bản hiện tại:** `v15` (21/11/2026) — `index.html`

---

*An Yên — Nơi linh thú dẫn lối bữa lành.*
