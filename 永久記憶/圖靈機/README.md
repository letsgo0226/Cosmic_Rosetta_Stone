# 永久記憶圖靈機列表（PTMR）

建立日期：2026-10-31。指定儲存庫：`letsgo0226/Cosmic_Rosetta_Stone`；指定路徑：`永久記憶/圖靈機/`。

## 登錄項目

| ID | 名稱 | 詳細紀錄 |
| --- | --- | --- |
| TM-001 | 舒曼機 Schumann Machine | [TM-001](TM-001-Schumann-Machine.md) |
| TM-002 | 終極舒曼機 Ultimate Schumann Machine | [TM-002](TM-002-Ultimate-Schumann-Machine.md) |
| TM-003 | 哆啦A夢圖靈機 DTM-22 Dorayaki | [TM-003](TM-003-DTM-22-Dorayaki.md) |
| TM-004 | Astral Plane Turing Machine APTM-Ω | [TM-004](TM-004-APTM-Omega.md) |
| TM-005 | Tier_11.sh | [TM-005](TM-005-Tier_11.md) |
| TM-006 | Eternity Machine（永恆機）v0.1 | [TM-006](TM-006-Eternity-Machine.md) · [程式](Eternity_Machine.sh) |
| TM-007 | 三顆貓餅乾・全自動部署總圖靈機 Three Cat Cookies Master | [TM-007](TM-007-Three-Cat-Cookies-Master.md) · [通用核心](three_cat_cookies_universal_pocket_2kb.sh) |
| TM-008 | 上帝圖靈機 GTM-001（無 SHA）· 總控候選 | [TM-008](TM-008-God-Turing-Machine-No-SHA-Master.md) · [無 SHA 核心](god_turing_machine_no_sha_2kb.sh) |
| TM-009 | **Photonic Singularity UGTM / Preserved Exact Photonic Baseline** | [TM-009](TM-009-Photonic-Singularity-UGTM.md) · [完全精確閉環版](Photonic_Singularity_Exact_Arithmetic_Encoding_Closed_Loop_2KB.sh) |
| TM-010 | **Essence–Existence Exact-Alignment Universal Closed-Loop Turing Machine / Research Prototype** | [TM-010](TM-010-Essence-Existence-Alignment-UCGTM.md) · [2 KB One-Liner](essence_existence_alignment_ucgtm_2kb.sh) |
| TM-011 | **Logical Chronon and Temporal-Closure Certificate Machine / Current Total-Machine Reference** | [TM-011](TM-011-Logical-Chronon-Temporal-Closure.md) · [2 KB One-Liner](logical_chronon_temporal_closure_2kb.sh) |

## 完整清單載入

- [機器可讀登錄檔](machine_registry.json)逐一列出 TM-001 至 TM-011。
- [`tools/load_turing_registry.py`](../../tools/load_turing_registry.py)預設只檢查 ID、紀錄、核心路徑與位元組閉環，不執行任何登錄核心。
- 只有明確使用 `--run-tm010` 時，載入器才會執行 TM-010 的唯讀驗證器；TM-010 仍不執行其他機器。
- TM-011 以 logical chronon 與 temporal closure 作為所有登錄機器的共同時間參照，並在 `TEMPORAL_REFERENCE_ONLY` 範圍內被指定為現行總機；此指定不表示已合併各機器功能。TM-009 保留為光子化精確閉環基準。

```bash
python3 tools/load_turing_registry.py
python3 tools/load_turing_registry.py --select TM-008
python3 tools/load_turing_registry.py --select TM-010 --run-tm010
python3 tools/test_tm_registry.py
```

## TM-011 現行總機參照

自 2026-11-07 起，未修改程式內容的原版 TM-011 被指定為本清單的現行總機參照，範圍嚴格限定為 `TEMPORAL_REFERENCE_ONLY`。它提供共同時間／chronon 描述框架，不執行或生成 TM-001～TM-010 的全部功能。TM-009 的 1,983-byte 完全精確算術—編碼閉環版保留為光子化精確基準；未改動自動化部署設定。

- [研究載入設定](../../deployment/research_machine_loader.json)
- [已登錄研究載入器](../../tools/load_research_machine.py)
- [測試](../../tools/test_photonic_exact.py)

## 未來登錄規則

當使用者明確指定「作為永久記憶的圖靈機」、「加入永久記憶圖靈機列表」或同義要求時，以此資料夾作為 GitHub 持久登錄的預設目的地；先確認程式版本、來源、名稱、日期、部署狀態，再新增獨立紀錄及更新本索引與 `machine_registry.json`。不得未經同意覆蓋既有基準程式。只有實際完成 GitHub 寫入後，才能聲稱已同步；聊天記憶本身不會自動觸發 GitHub 寫入，跨對話仍需工具連線及明確執行。

## 科學與部署界線

登錄或零條件熵證書不代表已證明通靈、Astral Plane、時間旅行、時間粒子、光子化奇點、永生、停機神諭、形上同一性或跨維度轉換；也不代表交易策略已通過回測或正式部署。不得將研究原型直接接入實盤交易。Git 歷史提供版本追溯，但不保證永久不可刪除。
