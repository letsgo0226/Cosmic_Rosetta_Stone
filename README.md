# Cosmic_Rosetta_Stone

本倉庫以 **通用上帝圖靈機（Universal God Turing Machine；UGTM）** 作為全自動部署系統的總圖靈機。現行實作為 v4.5 LMN-Church-Turing-Kleene；K-GTM v4.3 保留為其固定點核心。

- [圖靈機記憶清單](TURING_MACHINE_MEMORY.md)
- [克萊尼上帝圖靈機正式定義](docs/GTM_G_CANONICAL_DEFINITION.md)
- [總圖靈機部署指標](deployment/total_turing_machine.json)
- [UGTM v4.5 單行實作](machines/UGTM_v45_2KB.sh)
- [UGTM 通用性範圍](docs/UGTM_UNIVERSALITY_SCOPE.md)
- [K-GTM v4.3 固定點核心](machines/K-GTM_v43_LMN_KRT_2KB.sh)
- [GTM-G v4.2 quine 基準](machines/GTM-G_v42_2KB.sh)

每次相關檔案推送至 main 時，GitHub Actions 會自動驗證完整八指令語義、閉合程式輸出、輸入指令、總機指標與安全標記，然後發布可下載的已驗證成品。

## 光子化奇點圖靈機（TM-009，精確版研究載入）

**現行 TM-009 精確編碼研究入口：** [1,318-byte UGTM–UCP Exact Encoding](machines/UGTM_UCP_Exact_Encoding_2KB.sh)。它以精確的有理數和符號表達式追蹤固有時間平方、三態機率、資訊熵表達式及 G257 可逆編碼。

**浮點歷史研究原型：** [1,934-byte Photonic Singularity UGTM](machines/Photonic_Singularity_Universal_God_Turing_Machine.sh)；兩份程式均已另外保存於 `永久記憶/圖靈機/`。

[TM-009 永久機型紀錄](永久記憶/圖靈機/TM-009-Photonic-Singularity-UGTM.md) · [研究載入指標](deployment/research_machine_loader.json) · [精確驗證測試](tools/test_photonic_exact.py)

在儲存庫根目錄執行 `python3 tools/load_research_machine.py` 僅核對身份；`python3 tools/load_research_machine.py --run 10 0.6 0.3 1` 才實際執行精確版本（最後參數為 `u`，非舊版的 `omega`）。**正式總圖靈機 UGTM v4.5 及其既有自動部署基準不變**。這些模型不證明時間粒子或真正的光子化奇點。

## DTM-22 protective computation research (2026-11-06)

A new **side-effect-free experimental protection layer**, based on the existing TM-003 Doraemon three-phase token model and TM-007 verify-before-deploy design, is now available. It verifies selected TM-009 exact symbolic certificates without replacing any original machine or deployment setting.

- [English research specification (.txt)](research/Protective_Computation_and_State_Integrity.txt)
- [Python state guardian and TM-009 certificate validator](tools/dtm_protective_core.py)
- [Adversarial regression tests](tools/test_dtm_protective_core.py)
- [Protective CI workflow](.github/workflows/verify-dtm-protection.yml)

Run `python3 tools/dtm_protective_core.py --fault drop --restore` to observe a denied invalid proposal and a logical checkpoint restoration. Run `python3 tools/test_dtm_protective_core.py` for tests. **The project does not claim actual time travel, consciousness preservation, physical shielding, or perfect security.** The original TM-003, TM-009, UGTM v4.5, and Schumann baselines are unchanged.

## DTM-22 guarded-transition formal verification (2026-11-06)

The independent DTM-22 protective module has passed an abstract **Z3 QF_LIA** safety verification over unbounded mathematical integers: **13 UNSAT safety-counterexample queries, 3 SAT valid-transition witnesses, and 1 SAT counterexample for a deliberately weakened rule**. A separate set of **13 Python regression tests** also passed in [GitHub Actions](https://github.com/letsgo0226/Cosmic_Rosetta_Stone/actions/runs/42065274503).

- [Formal verification technical report (.txt)](research/DTM22_Formal_Verification.txt)
- [Machine-checkable SMT model in Python](tools/prove_dtm_invariants.py)
- [Versioned observed results summary](docs/dtm22_formal_evidence.json)
- [Protected state machine](tools/dtm_protective_core.py)
- [Proof workflow](.github/workflows/verify-dtm-protection.yml)

The proof concerns the stated **abstract logical transition model** and its state invariants. It is **not** a formally verified refinement of the entire Python interpreter, a cryptographic authentication proof, a quantum/physical safety guarantee, or a deployment authorization. TM-003, TM-007, TM-009 and the UGTM v4.5 canonical deployment remain distinct and unchanged.
