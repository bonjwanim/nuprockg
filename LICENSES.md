# 라이선스 행렬 — NuProc Ontology / NuProcKG

> 이 저장소는 **뉴스 제공자가 공급한 record 를 한 건도 재배포하지 않는다.**
> 아래 라이선스는 저자가 권리를 가진 것 — 온톨로지, 코드, 문서, 합성 예제,
> 사례 수준 집계 — 에만 적용된다. 그중 공개 저장소에 싣는 것과 요청 시 제공하는 것은
> §1 의 '공개 저장소' 칸이 정한다.

---

## 1. 행렬 — **공개 범위의 정본**

**이 표가 무엇이 공개되고, 무엇이 요청 시 제공되며, 무엇이 배포되지 않는가의 정본이다.** `README.md` 의
*What is in this release* · *Access* 는 이 표를 따르고, **어긋나면 이 표가 이긴다.**

> **공개 범위.** 공개 저장소에는 **네 모듈 (+ `CHECKSUMS.txt`) · 문서와 메타데이터 · 이 판의
> CQ 질의 · 합성 데모 그래프 · 합성 시험 자료** (`tests/` — 2026-10-29 저자 결정) 만 싣는다 — 코딩 파이프라인이나 원자료를
> 드러내지 않으면서 원고의 패키지 주장과 평가를 지탱한다. **코딩 프롬프트 · 코딩 · 검증 규약 · 분석 코드 · 평가 기록**
> (레지스트리 · 집계 스냅숏 포함) 과 ADR · 앞 판은 **교신저자에게 합당한 요청이 있으면 제공한다** — 진행 중인 박사논문 연구의 일부이기 때문이다. 요청 시
> 제공은 저자의 저작물에만 해당한다. record 수준 자료와 기사는 요청해도 제공할 수 없다 (§2). 사람 이름 표기가 든 파일 (행 16) 은 어느 것도
> 공개 목록에 없다.

| # | artifact | 공개 저장소 | 라이선스 | 근거 |
|---|---|---|---|---|
| 1 | **온톨로지 네 모듈** `ontology/nuproc-{core,codebook,alignments,shapes}.ttl` · `ontology/CHECKSUMS.txt` | **공개** | **CC BY 4.0** | 저자 저작물. `dcterms:license` 로 **네 모듈 헤더에 각각 선언**돼 있다 |
| 1b | **시험 그래프 (개발 저장소의 원본) · 앞 판** `ontology/fixtures/**` · `ontology/versions/**` · `ontology/CHECKSUMS-v*.txt` · `ontology/imports/**` | 요청 시 제공 (시험 그래프는 행 1c 의 공개 사본이 같은 그래프다) | **CC BY 4.0** (앞 판은 동결 당시 바이트 그대로 · 외부 어휘 사본은 그 원 라이선스) | 원본의 주석은 한국어 개발 기록이다 |
| 1c | **합성 시험 자료** `tests/**` — SHACL 시험 그래프 112 (`tests/fixtures/` — 원본과 같은 그래프, 주석을 영어 머리 주석으로 바꾼 사본) · 기대 판정표 `EXPECTED.csv` · 실행기 `run_fixtures.py` · 같은 사례 대조 예 `tests/composition_example/` (`evaluation/comparative/v0.8/composition_example/` 의 바이트 그대로의 사본 — 원고 초안 `supplement_section.tex` 는 뺀다) · `README.md` | **공개** (2026-10-29 저자 결정) | **CC BY 4.0** (그 안의 Python 스크립트 셋 — `run_fixtures.py` · `run.py` · `check_terms.py` — 도. 공개 저장소의 라이선스는 뿌리의 `LICENSE` 하나이고, 대조 예의 스크립트는 원본 자리에서도 행 8 (CC BY 4.0) 이다) | 합성 자료 — 실제 조직 · 기사 · 사건 0. `scripts/build_public_tests.py` 가 만들고 `check_release` P12 가 원본과 대조한다 |
| 2 | **온톨로지 문서** `docs/ontology/index.html` | **공개** | **CC BY 4.0** | 모듈에서 생성한 문서 |
| 2b | **설계 기록 · 평가 규약 · 개발 문서** `docs/adr/**` · `docs/EVALUATION_PROTOCOL.md` · `docs/*.md` | 요청 시 제공 (ADR · 평가 규약 — 보충이 근거로 가리킨다) · 공개하지 않는다 (그 밖 개발 문서) | **CC BY 4.0** | 저자 저작물. 온톨로지가 ADR 을 IRI 로 가리키며, w3id 규칙이 그 IRI 를 README 의 *Design records* 로 보낸다 |
| 3 | **코드** `scripts/**`, `run_public_demo.sh`, `run_private_full.sh` | 요청 시 제공 | **MIT** (`LICENSE`) | 분석 코드 (빌드 · 검증 · 평가 · 검사) |
| 4 | **질의** `queries/v0.9/**/*.rq` · `queries/examples/*.rq` | **공개** | **CC BY 4.0** | 이 판의 역량 질문 · 시연 질의 · 그림 1c 질의 · 사용 예 질의 셋 (G7~G9 — 보충 S4). 앞 판의 질의와 결과 파일은 요청 시 제공 |
| 5 | **합성 demo 그래프** `kg/public/nuproc-demo.ttl` | **공개** | **CC BY 4.0** | 출처인 `replication_package_v1.0/data/synthetic_sample/` 이 저자가 **CC BY 4.0 으로 라이선스한** 합성 표본이다 (그 패키지 자체는 아직 기탁되지 않았다). 실제 사건·기사·행위자가 **0건** |
| 6 | **벤치마크 스냅샷** `data/derived/benchmark_snapshot/**` | 요청 시 제공 | **CC BY 4.0** (승계) | 원 패키지가 CC BY 4.0 으로 라이선스한 사례 수준 집계표의 사본. 자체 `LICENSES.md` 동봉 |
| 7 | **레지스트리** `registry/**` | 요청 시 제공 | **CC BY 4.0** | 저자가 만든 통제어휘 · 행위자 권위 표 · 코드북. record 가 아니다. 행위자 표의 다섯 표기에 사람 이름이 든다 (원고 윤리 선언) |
| 8 | **평가 산출물** `evaluation/**` | 요청 시 제공 | **CC BY 4.0** | 저자가 만든 규약 · 지표 · 판정 · 근거 · 동결 목록. record 식별자를 담지 않는다 |
| 9 | **실행 로그·회귀 기록** `results/**` | 요청 시 제공 | **CC BY 4.0** | 검사·평가 실행의 기록물 |
| 10 | **릴리스 준비물** `release/w3id/` · 검토자 표 `release/reviewer_data/` | 공개 저장소에 싣지 않는다 — w3id 규칙은 제출물로 따로 간다 (w3id 에 내는 것은 `htaccess` 와 영어 `nuproc-README.md` — 관리자 · 연락처). `release/reviewer_data/` 는 평가 기록으로 요청 시 제공 | **CC BY 4.0** | 저자 저작물 |
| 11 | **실행 환경 고정** `environment/**` | 요청 시 제공 (코드와 함께) | **MIT** (`LICENSE`) | 코드에 딸린 빌드 · 의존성 고정 파일 |
| 12 | **최상위 문서** `README.md` · `CHANGELOG.md` · `CITATION.cff` · 이 파일 · `.gitattributes` | **공개** | **CC BY 4.0** | 저자 저작물 · 메타데이터. 공개 저장소의 `CHANGELOG.md` 는 판마다 바뀐 것만 적은 영어 판이다 (`release/public-package/CHANGELOG.md` — 개발 저장소의 `CHANGELOG.md` 는 개발 기록이다) (`.gitattributes` 는 줄끝 설정 — 공개 저장소의 라이선스는 뿌리의 `LICENSE` (CC BY 4.0 전문, 행 12c) 하나이므로 다른 공개 파일과 같이 CC BY 4.0) |
| 12b | **개발 기록** `PLAN.md` · `STATE.md` | 공개하지 않는다 | **CC BY 4.0** | 개발 기록 |
| 12c | **공개 저장소의 `LICENSE`** `release/public-package/LICENSE` — 공개 묶음이 공개 저장소 뿌리의 `LICENSE` 로 옮긴다 | **공개** (뿌리의 `LICENSE`) | 법률 전문 자체는 Creative Commons 가 CC0 로 공중 영역에 두었다 | Creative Commons 의 CC BY 4.0 `legalcode.txt` 그대로 (sha256 `9ba9550a…`). GitHub 이 저장소의 라이선스로 읽는 파일이다 — 이 표는 그렇게 읽히지 않는다. 개발 저장소의 `LICENSE` (MIT, 행 3) 는 코드의 것이라 공개 저장소에 싣지 않는다 |
| 13 | **원고 초고** `paper/**` (골격 `.tex` · 표지 · 커버레터 · 번역 대응표) | **배포하지 않는다** | — | 권리 문제가 아니라 **저널 정책** 때문이다. Sage 는 투고본·수리본의 재이용을 **비상업·개작 금지**로 제한해 이 저장소의 CC BY 4.0 과 충돌하고, Sage 자신의 preprint 정의(*preprint platform and SCNs*)가 **코드 저장소를 포함하는지 정하고 있지 않다.** 공개 저장소에는 원고가 없다 |
| 14 | **전체 ABox** `kg/private/**` | **배포하지 않는다** | — | (iii)층 record 수준. §2 참조 |
| 15 | **원자료** `data/raw/**` | **배포하지 않는다** | — | (i)(ii)층. 제공자 약관 §5·§6 |
| 16 | **사람 이름 표기가 든 파일** — 행위자 레지스트리의 다섯 표기 (사람 이름) 와 같은 표기가 든 추적 파일 31개 (보고서 · ADR 셋 · 로그 · 레지스트리의 다른 표 · 스크립트 · CQ02 결과 · `STATE.md` · AI 사용 기록) | **공개 저장소에 싣지 않는다** | — | 개인정보. 레지스트리 (`registry/actor_mentions.csv`) 도 공개 목록에 없다 (행 7) |

### 1.1 포괄 조항 — 이 표에 행이 없는 것

행렬에 빠진 추적 파일이 있으면 **재사용 조건 없이 공개되는 자리가 생긴다.** 표를 채우는 것이 원칙이고, 새
산출물이 생겨 표가 아직 따라오지 못한 동안의 기본값은 다음과 같다.

- **코드로 실행되는 것** (`*.py` · `*.sh` · 빌드·의존성 설정) — **MIT** (`LICENSE`)
- **그 밖의 저자 저작물** (문서 · 어휘 · 질의 · 집계·합성 데이터) — **CC BY 4.0**
- **저장소 설정 파일** — `.gitignore` 는 코드에 준해 **MIT** (공개 저장소에 없다). `.gitattributes` 는 공개 저장소에
  실리므로 행 12 를 따른다 (CC BY 4.0)
- **제공자 유래 record 수준 자료** — **어떤 라이선스도 부여하지 않는다.** 배포 대상이
  아니다. 기본값이 '공개' 쪽으로 흐르지 않는다는 것이 이 조항의 요점이다

---

## 2. 왜 record 를 배포하지 않는가

제공자(NewsAPI.ai / Event Registry) 약관이 **record 뿐 아니라 dataset·metadata·
derivatives 까지** 재배포 대상에 넣는다. 그래서 **record 수준은 전량 비공개**이고
저자의 저작물만 공개하거나 (§1 의 '공개' 행) 요청 시 제공한다. 이 판정은 이 프로젝트가 새로 내린 것이 아니라
기존 `replication_package_v1.0` (저자가 CC BY 4.0 / MIT 로 라이선스했으나 아직 기탁되지 않았다 — §3) 이 적용한 것과
**같은 판정**이다.

**구독 등급.** 수집 당시 구독은 **유료
등급**이었다. 약관 §3 이 무료 등급을 *"solely for evaluation and testing"* 으로
한정하며 research 사용을 금지하므로 이 확인이 필요했다. 유료였으므로 **§5 의 이용
라이선스가 적용**되고, 위 판정(record 비공개)이 그대로 선다. 집계 스냅숏 · 평가 기록은 요청 시 제공하고, 합성 데모 그래프는 공개한다 (§1).

---

## 3. 기존 두 `LICENSES.md` 와의 관계

| 파일 | 무엇 |
|---|---|
| `data/replication_package_v1.0/LICENSES.md` | **선행 연구 패키지.** 저자가 CC BY 4.0 / MIT 로 라이선스했으나 **아직 기탁되지 않았다** |
| `data/derived/benchmark_snapshot/LICENSES.md` | 그 패키지에서 뜬 벤치마크 사본 |
| **이 파일** | **온톨로지 산출물** 전체의 행렬 |

**정합한다.** 기존 패키지가 쓴 것이 정확히 **데이터·문서 CC BY 4.0 / 코드 MIT**
이고, **온톨로지도 같은 짝을 택했다.** 세 문서가 같은 규칙을 말하며 서로 어긋나는 조항이 없다.

**한 가지 다른 점**은 온톨로지가 선행 패키지의 산출물이 아니라 **별도 저작물**이라는
것이다. 그래서 라이선스를 승계하지 않고 **독립적으로 부여**하며, 두 산출물의 관계는
`docs/DATA_AVAILABILITY_DRAFT.md` 와 `docs/CONTRIBUTION_AND_OVERLAP.md` 가 서술한다.

---

## 4. 인용

`CITATION.cff` 를 쓴다. CC BY 4.0 은 **귀속(attribution)을 요구**하므로 온톨로지를
재사용할 때 저자와 버전을 밝혀야 한다.

**CC0 를 택하지 않은 이유.** 어휘에는 귀속 중첩을 피하려 CC0 를 권하는 견해가 있다.
그럼에도 CC BY 4.0 을 택한 것은 **기존 패키지와 같은 라이선스로 묶어** 두 산출물의
관계를 설명하기 쉽게 하기 위해서다.

---

## 5. 아직 붙지 않은 것

| 항목 | 상태 |
|---|---|
| **DOI** | 쓰지 않는다 — 보관 DOI 없이, 공개 판은 저장소의 태그 `tbox-v0.9.0` 으로 고정한다 (ADR-0042) |
| **`https://w3id.org/nuproc/` 등록** | 미등록. 저장소 공개와 함께 신청한다 |
| **ORCID** | 제공되지 않았다. **지어내지 않는다** — `CITATION.cff` 와 온톨로지 헤더 양쪽에서 비워 둔다 |

**이 세 가지가 비어 있다는 사실 자체를 숨기지 않는다.** w3id 등록과 ORCID 는 공개 시점에 채우고, DOI 는 쓰지 않는다.
