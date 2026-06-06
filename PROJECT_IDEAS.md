# 💡 Project Ideas — AMD Developer Hackathon ACT II

> Ý tưởng được lọc qua **Updated Winning Strategies** (WINNING_STRATEGIES_AMD_ACT_II.md) + AMD ACT I winners patterns + MI300X strengths (192GB VRAM, bare-metal perf, ROCm).

Mỗi ý đều nhắm:
- Pain point cụ thể + shock metric.
- Genuine agentic + deep AMD (ROCm/MI300X) integration.
- 1 WOW performance/agentic moment.
- Production signals + easy judging.
- Phù hợp 5 ngày + $100 credits.

---

## Tier S (Rất mạnh, dễ adapt theo track TBA)

### 1. Enterprise Meeting Intelligence → Production Workflows (CogniCore 2.0)
**Hook**: "Meetings tốn hàng giờ mỗi tuần. CogniCore 2.0 biến 1 giờ meeting thành production-ready workflows, tasks, risks, docs — chạy real-time trên MI300X với full context."

**Pain + Metric**:
- Pain: Meeting notes bị quên, requirements bị mất, risks không được track → delay và rework (doanh nghiệp mất hàng chục nghìn USD/năm).
- Shock: "1h meeting → actionable artifacts + assignments + risk report trong <90 giây."

**AMD Angle (deep)**:
- Dùng large reasoning model (70B+ class) **với context dài** (MI300X 192GB cho phép ít quant hơn hoặc full long-context cho transcript + history).
- Multi-agent crew (intake → extractor → risk analyst → task planner → writer) chạy parallel nhanh nhờ GPU power.
- Real-time streaming (audio → transcript → agents update live).
- Optional: Fine-tune nhỏ specialist agent trên domain data.

**WOW Moment**:
- Agents "suy nghĩ" visible + output xuất hiện real-time trong lúc meeting diễn ra (hoặc replay).
- GPU utilization dashboard + "processed X meetings/hour on single MI300X".

**Agentic Elements**:
- Genuine tool calling (query past meetings memory, search internal knowledge, generate tickets).
- Cross-agent collaboration + memory passing.
- Learning: Adjust extraction weights dựa trên user feedback/accepted tasks.

**Production**:
- Demo mode với pre-loaded transcripts.
- JUDGING.md + health + replay endpoint.
- Deploy trên AMD Cloud.

**Risk/Feasibility**: Cao nhưng có precedent (CogniCore thắng ACT I). Tập trung 1-2 core agents + streaming trước.

---

### 2. HIP-Hop 2.0 — Autonomous CUDA-to-ROCm Migration Swarm (Siêu AMD-native)
**Hook**: "CUDA vendor lock-in đang giết chết nhiều project. Một swarm agents tự phân tích, port, test, benchmark và deliver working ROCm/HIP version — trên chính MI300X."

**Pain + Metric**:
- Pain: Porting CUDA sang AMD tốn hàng tuần/tháng của engineers.
- Shock: "Paste GitHub repo CUDA → production-ready ROCm version + benchmark report + migration log trong <10-30 phút."

**AMD Angle (rất sâu)**:
- Swarm agents chạy **trên MI300X** để tự test performance.
- Dùng ROCm tools (hipify, etc.) + LLM reasoning.
- Agents tự viết kernel tối ưu, chạy benchmark (throughput, memory, util), so sánh trước/sau.
- Capture real profiling data (rocm-smi, traces) làm bằng chứng.

**WOW Moment**:
- Live migration + benchmark dashboard update real-time.
- "Before (CUDA on NVIDIA) vs After (ROCm on MI300X)" side-by-side với numbers đẹp.

**Agentic Elements**:
- Multiple specialist agents (Analyzer, HIP Translator, Tester, Optimizer, Documenter).
- Tool calling thực (chạy compiler, chạy tests, parse errors, edit code).
- Self-improvement: Học từ lỗi porting trước.

**Production**:
- Demo với vài repos phổ biến (hoặc synthetic kernels).
- Full artifacts: diff, logs, benchmarks.

**Risk/Feasibility**: Rất "on-brand" cho ACT II. Có precedent (HIP-Hop trong ACT I). Có thể scope nhỏ (một module quan trọng) + show process rõ.

---

### 3. High-Throughput Multi-Agent Decision Engine (FinOps / Trading / Ops)
**Hook**: "Quyết định phức tạp trong môi trường thay đổi nhanh cần nhiều góc nhìn. Một crew agents phân tích song song trên MI300X, đưa ra quyết định với uncertainty + audit trail — với throughput cao gấp X lần."

**Pain + Metric**:
- Pain: FinOps / trading / operations decisions chậm, thiếu context, dễ bias hoặc miss risk.
- Shock: "X concurrent analyses + risk-gated decision trong Y giây trên single MI300X."

**AMD Angle**:
- Chạy nhiều specialist agents (market analyst, risk, compliance, executor) **parallel** nhờ VRAM lớn và compute.
- Large "orchestrator" model với long memory của past decisions.
- Real-time data ingestion + low-latency inference.
- Benchmark: agents/sec, decisions/sec, GPU util.

**WOW Moment**:
- Dashboard live: nhiều agents "suy nghĩ" cùng lúc → consensus hoặc flagged divergence → action.
- "4.4x throughput" style claim với evidence.

**Agentic**:
- Genuine collaboration + debate (adversarial agents).
- Memory of past outcomes → weight adjustment (learning loop).
- Circuit breakers / trust gates (deterministic verifier).

**Production**:
- Demo seed với historical scenarios.
- Full audit log.

**Risk**: Phù hợp track AI Agents + High-Perf. Dễ khoe perf metrics.

---

## Tier A (Mạnh, dễ làm đẹp)

### 4. Large-Context Multimodal Document Intelligence at Scale
**Hook**: "Tài liệu dày + hình ảnh + bảng biểu tốn hàng giờ để đọc và tổng hợp. Crew agents xử lý full fidelity trên MI300X và deliver structured intelligence report + citations trong <60 giây."

**AMD Fit**: 192GB cho phép xử lý nhiều pages/images cùng lúc mà không cắt xén (vision models full res + long reasoning context).

**WOW**: Speed + quality (so sánh với "thông thường phải quant nặng").

### 5. Uncertainty-Aware Clinical / Diagnostic Multi-Agent (nâng cấp ClinSight)
**Hook**: "Chẩn đoán y khoa cần biết 'chúng ta chắc chắn bao nhiêu'. Multimodal agents (notes + imaging + labs) chạy trên AMD với explicit uncertainty quantification và second-opinion agents."

**AMD Fit**: Multimodal heavy + real medical impact (thắng cao ở ACT I).

### 6. Self-Optimizing Inference / Agent Workload Tuner
**Hook**: "Chạy AI workloads trên GPU thường tốn kém và suboptimal. Một meta-agent liên tục benchmark, profile, propose optimizations (quant, batching, kernel, scheduling) và apply — trên chính MI300X."

**Rất on-brand** cho "high-performance" focus của ACT II.

---

## Tier B (Độc đáo, có thể bùng nổ nếu execution tốt)

- **Adversarial Red Team cho AI Systems trên AMD**: Crew agents tấn công strategy / prompts / outputs của hệ thống khác (giống RedTeam winners) nhưng chạy inference heavy trên MI300X.
- **Real-time Multi-Agent Simulation / Scenario Planner**: Dùng GPU power để chạy nhiều simulation song song (finance, logistics, robotics synthetic).
- **Knowledge Graph + Agent Memory on Big Context**: Agents xây dựng và query knowledge graph từ data domain, tận dụng context window lớn.

---

## Hướng dẫn chọn & tiếp theo

1. **Chọn dựa trên**:
   - Bạn mạnh gì (agents vs low-level perf/optimization vs multimodal)?
   - Track nào nhiều khả năng (khi TBA ra thì pivot).
   - Dễ demo WOW trong 5 ngày.

2. **Bước tiếp theo cho ý bạn thích**:
   - Viết 1-page PRD / spec (pain, narrative, agent roles, AMD angle, WOW, tech choices).
   - Tạo architecture diagram + JUDGING.md draft.
   - Chọn 1-2 repos/tools starter (ví dụ vLLM ROCm examples, CrewAI templates).

Bạn thích ý nào nhất (hoặc muốn mix)? 
Mình có thể:
- Deep dive 1-2 ý (viết chi tiết agent prompts, tech stack, risks, 5-day plan).
- Tạo template README + JUDGING.md cho ý đó.
- Nghiên cứu thêm AMD-specific tools (vLLM trên ROCm, SGLang, profiling commands, etc.).

Cứ nói mình làm tiếp ngay. Chúc bạn build ra project top-tier! ⚡
