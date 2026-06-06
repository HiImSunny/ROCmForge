# 🏆 Updated Winning Strategies — AMD Developer Hackathon ACT II (July 2026)

> Tổng hợp từ:
> - Nghiên cứu chi tiết previous hackathons của bạn (AI Agent Olympics, AMD ACT I, IBM Bob, Transforming Enterprise, v.v. trong `HACKATHON_WINNING_RESEARCH/`)
> - Phân tích winners AMD ACT I (CogniCore, ClinSight, HexySAR...)
> - Fresh signals từ web (recap ACT I, official posts ACT II, MI300X strengths 2026)

**Mục tiêu**: Cập nhật những gì vẫn đúng + những gì cần "thêm" cho ACT II (focus high-perf + agents trên MI300X + ROCm).

---

## 1. Core Winning Formula (Vẫn đúng 90% từ previous research)

Từ hàng chục winners (Deals Machine, Cascade AI, CogniCore, Trellis...):

```
WINNING FORMULA (AMD ACT II version) =
  1 pain point doanh nghiệp cụ thể + shock metric + real case
  + Genuine agentic workflow (real tool calling + decision making)
  + Deep AMD integration (không chỉ "gọi API")
  + Production-ready + Demo mode (seed/replay + health)
  + 1 WOW real-time / performance / speed feature
  + README xuất sắc + JUDGING.md (copy-paste verification)
  + Narrative mạnh: "[Shock metric]. [Real case]. Our agents [solves it] in [time] on MI300X."
  + Learning / memory / self-improvement loop
```

**Vẫn cực kỳ quan trọng**:
- **Genuine agentic** > Hardcoded pipelines (LLM tự chọn tool, requestMoreContext, cross-agent collab).
- **≥2 "sponsor" angles** (ở đây là AMD + một cái khác: ví dụ AMD + multimodal model, hoặc AMD + agent framework sâu, hoặc AMD + real-world data/integration).
- **Production signals**: Docker, health endpoint, deployment guide, CI/CD.
- **JUDGING.md** là game-changer (vì nhiều judges/LLM graders chỉ skim).
- **Demo mode** không phụ thuộc external services (rất quan trọng cho 5-day hackathon).

---

## 2. AMD-Specific Upgrades (Những gì cần "thêm" cho ACT II)

Từ AMD ACT I winners analysis + fresh data:

### A. Show AMD Love — Explicit & Measurable (Bắt buộc cho top placements)
- **Không chỉ** "chạy trên AMD Cloud".
- **Phải**:
  - Nói rõ dùng **ROCm** (version nếu có).
  - Chạy inference / agents / fine-tune **trên MI300X**.
  - **Show metrics**: GPU utilization, memory bandwidth, throughput (tokens/s, agents concurrent, images/s), latency, power/thermals.
  - So sánh (nếu có): "X times faster than quantized on consumer GPU" hoặc "handle 70B+ model with full context vs heavy quant elsewhere".
  - Profiling artifacts (nếu làm được nhanh: vLLM/SGLang logs, rocm-smi, etc.).

**Ví dụ thực tế từ ACT I + signals**:
- CogniCore: Heavy multi-agent + real-time trên AMD.
- ClinSight: Multimodal + uncertainty quantification **on AMD hardware**.
- Một số project: Fine-tune Qwen trên MI300X (loss curves), HIP-Hop (CUDA → ROCm migration swarm), 4.4x throughput claims với FP8 trên MI300X.

**ACT II advantage**: MI300X có **192GB VRAM** → đây là super power.
- Chạy large reasoning models (70B+) **với ít quantization hơn** hoặc full context.
- Multi-agent crews chạy parallel thoải mái.
- Long-context agents (research, coding, complex planning) hoạt động tốt hơn rõ rệt.
- Vision/multimodal ở full resolution hoặc nhiều images cùng lúc.

### B. Performance / High-Perf là Feature (ACT II khác ACT I một chút)
ACT II nhấn mạnh: "Bigger AI workloads. Faster GPUs. Bare-metal AMD performance. Real compute. Not a sandbox."

Chiến thuật thêm:
- Làm **performance-critical** agents hoặc workflows (ví dụ: real-time multi-agent decision systems, large-scale document intelligence, simulation agents, trading/FinOps với high throughput).
- **Benchmarking as storytelling**: "Before/after" hoặc "single GPU vs previous setups".
- CUDA-to-ROCm migration agents (HIP-Hop style) là ý tưởng cực AMD-native.
- Fine-tuning nhanh + serving, hoặc inference optimization (quant, speculative decoding, PD disaggregation hints, v.v.).
- "Cost/performance" angle: Chạy được nhiều concurrent agents / heavy workloads với chi phí thấp hơn (dùng $100 credits + MI300X power).

### C. Agentic + AMD Synergy (Best of both worlds)
Kết hợp 2 trend mạnh nhất:
- **Genuine multi-agent** (AutoGen, CrewAI, custom tool-calling crews, adversarial teams, etc.).
- Chạy trên **MI300X power** (large "brain" model không bị cắt xén, nhiều specialist agents chạy song song, long memory/context, multimodal agents).

Ví dụ patterns thắng:
- Multi-agent document intelligence (vision + reader + analyst + reporter) hoàn thành trong <60s.
- Meeting → workflow agents real-time.
- Uncertainty-aware medical agents.
- Migration / optimization swarms.

### D. Enterprise / Real Impact > Toy (Từ ACT I + general)
- B2B / enterprise pain points thắng cao hơn (CogniCore, ClinSight, OncoTriage).
- High-stakes domains: medical, finance/compliance, legal, robotics/SAR, security, operations.
- Quantified value: tiền tiết kiệm, thời gian giảm, risk giảm, throughput tăng.

---

## 3. Presentation & Judging Hacks (Vẫn là 50%+ chiến thắng)

Từ JUDGING_PATTERNS.md và winners:
- **README** là thứ judges đọc nhiều nhất (70% judges không chạy code).
- **JUDGING.md** với:
  - Elevator pitch 3 câu.
  - 90-second verification path (health + demo/seed + demo/replay).
  - Copy-paste curl commands.
  - Code map (file nào làm gì).
  - Honest limitations + feature matrix (✅/🔶/🔲).
- **Video demo** phải có **WOW moment** rõ ràng trong 30-90 giây đầu (real-time update, agents chạy parallel visible, speed ấn tượng, GPU metrics đẹp).
- Narrative 1 câu hook ngay đầu README.
- Architecture diagram (Mermaid hoặc ASCII).
- Deployment evidence (live URL + health).

**Đặc biệt cho AMD**:
- Screenshot rocm-smi / utilization / benchmarks trong README + video.
- Nói rõ "Running natively on AMD Instinct MI300X via ROCm on Developer Cloud".

---

## 4. Checklist Riêng cho AMD ACT II (5 ngày)

**Trước khi code (1-2h)**:
- [ ] Chọn 1 pain point cụ thể + shock metric + case study thực tế.
- [ ] Xác định "AMD angle" mạnh (large model, multi-agent parallel, real-time inference, optimization/migration, multimodal trên big VRAM, fine-tune + serve, etc.).
- [ ] Lên kế hoạch ≥1 deep AMD integration + 1 "WOW performance/agentic" moment.
- [ ] Viết draft narrative + JUDGING.md skeleton.

**Trong build**:
- [ ] Genuine agentic (tool calling thực, không hardcode).
- [ ] Chạy thực trên AMD Cloud / MI300X (dùng credits ngay từ đầu).
- [ ] Capture metrics & screenshots (GPU util, throughput, memory).
- [ ] Implement demo/seed + demo/replay endpoints.
- [ ] Health endpoint + logging.
- [ ] Viết README + architecture diagram song song.
- [ ] Learning/memory loop (nếu fit).

**Trước submit**:
- [ ] Live demo ổn định (không external dependency chết).
- [ ] Video có audio + rõ WOW + AMD metrics.
- [ ] JUDGING.md hoàn chỉnh.
- [ ] README pro (narrative, stack table, demo flow, AMD evidence, limitations honest).
- [ ] GitHub clean + LICENSE.

---

## 5. Common Pitfalls (Tránh)

- Chỉ "chạy được trên AMD Cloud" mà không show optimization/metrics (bị trừ điểm AMD track).
- Generic "multi-agent AI assistant" không có pain point cụ thể + metric.
- Hardcoded agent pipeline (judges phân biệt được).
- Demo chỉ chạy local hoặc phụ thuộc API key bên ngoài.
- README lười / thiếu demo flow / không có JUDGING.md.
- Quá tập trung model mà quên production signals + presentation.

---

## 6. Stack "Safe Bet" cho AMD ACT II (từ patterns)

- **Backend**: Python (FastAPI) hoặc Node (Fastify/Next API) — nhiều winners dùng cả hai.
- **Agents**: LangChain/LangGraph, CrewAI, AutoGen, hoặc custom tool-calling (tùy độ "genuine" bạn muốn khoe).
- **Inference trên AMD**: vLLM (nếu hỗ trợ tốt ROCm), SGLang, hoặc official AMD paths. Leverage 192GB VRAM cho large models.
- **Frontend**: Next.js + TS + Tailwind + shadcn (rất phổ biến và nhanh đẹp).
- **Deployment**: AMD Developer Cloud (bắt buộc show), có thể wrap Docker.
- **Extras mạnh**: Real-time (WebSocket/SSE), memory/vector (pgvector hoặc tương đương), benchmarking scripts.

---

**Nguồn chính**:
- Local: `HACKATHON_WINNING_RESEARCH/` (JUDGING_PATTERNS, WINNING_PATTERNS, ALL_WINNERS_DATABASE, AMD_ACT_I analysis, winning-formula).
- Local: `AI Agent Olympics Hackathon/analysis/`.
- Web: lablab.ai recap AMD Developer Hackathon, official ACT II posts, MI300X articles.

---

File này là "living document". Khi có track chính thức hoặc update mới từ Discord/lablab, mình sẽ bổ sung.

Bây giờ chuyển sang phần **Idea Generation**...
