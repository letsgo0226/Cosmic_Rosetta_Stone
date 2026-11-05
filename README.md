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

## 光子化奇點圖靈機（TM-009，研究載入）

[永久機型資料](永久記憶/圖靈機/TM-009-Photonic-Singularity-UGTM.md) · [研究版 2 KB 程式](machines/Photonic_Singularity_Universal_God_Turing_Machine.sh) · [載入設定](deployment/research_machine_loader.json)

以 `python3 tools/load_research_machine.py` 驗證內容身份；明確加上 `--run 10 0.6 0.3 0.2` 才執行。另有 [1,318 bytes 的精確有理數／符號編碼附件](machines/UGTM_UCP_Exact_Encoding_2KB.sh)，用於減少數學表示的浮點捨入。此登錄為總機研究入口，**不替換 v4.5 自動部署基準**；光子化奇點與時間粒子仍是研究假說。
