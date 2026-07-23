# Plan implementacji — System porównywania narzędzi AI do kodowania

**Wersja:** 1.1  
**Status:** gotowy do rozpoczęcia implementacji MVP  
**Data:** 13 lipca 2026  
**Dokument źródłowy:** `dokument_wymagan_system_porownywania_narzedzi_ai_v2.md`

## Spis treści

1. [Cel planu](#1-cel-planu)
2. [Przyjęte decyzje](#2-przyjęte-decyzje)
3. [Architektura docelowa MVP](#3-architektura-docelowa-mvp)
   - [3.1 Przepływ odpowiedzialności](#31-przepływ-odpowiedzialności)
   - [3.2 Komponenty](#32-komponenty)
   - [3.3 Struktura repozytorium](#33-struktura-repozytorium)
   - [3.4 Artefakty przebiegu](#34-artefakty-przebiegu)
   - [3.5 Skille użytkownika i CLI wewnętrzne](#35-skille-użytkownika-i-cli-wewnętrzne)
   - [3.6 Przepływ skilla `/tool-eval-research`](#36-przepływ-skilla-tool-eval-research)
   - [3.7 Przepływ skilla `/tool-eval-compare`](#37-przepływ-skilla-tool-eval-compare)
4. [Zakres MVP i odroczenia](#4-zakres-mvp-i-odroczenia)
5. [Plan prac](#5-plan-prac)
   - [Przyrost 1 — fundament projektu](#przyrost-1--fundament-projektu)
   - [Przyrost 2 — pełny research narzędzia](#przyrost-2--pełny-research-narzędzia)
   - [Przyrost 3 — porównanie i samowystarczalny HTML](#przyrost-3--porównanie-i-samowystarczalny-html)
   - [Przyrost 4 — obsługa operacyjna i dokumentacja](#przyrost-4--obsługa-operacyjna-i-dokumentacja)
   - [Przyrost 5 — ręczna akceptacja MVP](#przyrost-5--ręczna-akceptacja-mvp)
   - [Zależności między przyrostami](#zależności-między-przyrostami)
6. [Ryzyka i działania ograniczające](#6-ryzyka-i-działania-ograniczające)
7. [Macierz pokrycia kryteriów akceptacji Etapu 1](#7-macierz-pokrycia-kryteriów-akceptacji-etapu-1)
8. [Warunek rozpoczęcia i zakończenia implementacji](#8-warunek-rozpoczęcia-i-zakończenia-implementacji)

## 1. Cel planu

Plan opisuje architekturę, kontrakty danych, komponenty, kolejność prac, ograniczenia MVP, ryzyka i kryteria ukończenia Etapu 1. Rejestr decyzji zachowuje uzasadnienia oraz świadome odroczenia ustalone podczas sesji projektowej.

## 2. Przyjęte decyzje

### D-001 — Przenośność między harnessami agentowymi

**Status:** przyjęta  
**Decyzja:** rozwiązanie będzie repozytoryjnym zestawem skilli, definicji agentów i skryptów Python, możliwym do wykonywania przez różne harnessy agentowe, w szczególności Claude Code, Codex CLI oraz GitHub Copilot CLI.

**Konsekwencje:**

- logika domenowa i deterministyczna nie może zależeć od API pojedynczego harnessu;
- wspólne instrukcje przepływów będą utrzymywane w postaci neutralnych plików Markdown;
- elementy specyficzne dla harnessu będą cienkimi adapterami;
- skrypty Python otrzymają stabilny interfejs CLI i maszynowe wyniki;
- dane, konfiguracja i schematy pozostaną jednakowe niezależnie od użytego harnessu;
- kontrakty rdzenia pozostaną niezależne od LLM, aby po MVP można było dodać adaptery innych harnessów bez przebudowy modelu danych.

**Zakres MVP:** pierwsza wersja implementuje integrację wyłącznie z Claude Code. Codex CLI i GitHub Copilot CLI pozostają docelowym kierunkiem przenośności po ustabilizowaniu MVP.

### D-002 — LLM dostarczany przez harness

**Status:** przyjęta  
**Decyzja:** system nie wywołuje bezpośrednio API modeli. Całe rozumowanie LLM wykonuje model udostępniony przez harness. Instalacja nie wymaga klucza API ani SDK dostawcy modelu.

### D-003 — Agent wywołuje skrypty Python na żądanie

**Status:** przyjęta  
**Decyzja:** użytkownik wywołuje bezpośrednio skill operacji wysokiego poziomu, np. `/tool-eval-research X` albo `/tool-eval-compare A B`. Agent sam dobiera skille domenowe i wywołuje skrypty Python w momentach wymagających operacji deterministycznej. Skrypty są wewnętrznymi narzędziami agenta, a nie krokami wykonywanymi ręcznie przez operatora.

Kanonicznym interfejsem skryptowym będzie `python -m tool_eval <komenda>`. Większe dane będą wymieniane przez pliki JSON w izolowanym katalogu przebiegu. Python utrzymuje stan i wymusza obowiązkowe bramki, dlatego agent nie może pominąć walidacji, limitu napraw ani bezpiecznej publikacji przez staging, rollback i recovery.

### D-004 — Agent prowadzący i subagenci

**Status:** przyjęta  
**Decyzja:** skill wejściowy jest wykonywany w sesji agenta prowadzącego, który korzysta ze skilli domenowych, wywołuje skrypty i deleguje niezależne prace subagentom. Zakładamy użycie harnessu obsługującego subagentów.

Minimalny zestaw definicji agentów:

- `tool-eval-orchestrator` — agent prowadzący, właściciel przebiegu i punktu kuratorskiego;
- `tool-eval-worker` — generyczny subagent specjalizowany przez manifest zadania i wskazany skill.

Subagenci mogą równolegle odkrywać klasy źródeł, badać rozłączne paczki cech, wydobywać fakty i naprawiać niezależne rekordy. Nie modyfikują słownika, manifestu głównego ani aktywnego profilu. Scalanie, pełna walidacja, kuracja, flagi, porównanie i publikacja pozostają operacjami pojedynczego zapisującego. Python jest jedyną warstwą zapisującą dane trwałe.

### D-005 — Research wykonywany przez LLM

**Status:** przyjęta  
**Decyzja:** w Etapie 1 cały research — odkrywanie źródeł, przeglądanie treści, wyszukiwanie po znaczeniu i interpretacja — wykonują agent oraz subagenci przy użyciu narzędzi internetowych harnessu.

Python nie implementuje w Etapie 1 crawlera, lokalnego korpusu, BM25, embeddingów ani bazy wektorowej. Odpowiada za stan przebiegu, przygotowanie kontraktów, walidację, kontrolę kompletności śladu poszukiwania, scalanie, rewizje, flagi, świeżość, HTML i bezpieczną publikację. Lokalne pobieranie oraz indeksowanie pozostaje możliwym rozszerzeniem, jeśli pilotaż wykaże problem ze skalą, kosztem albo kompletnością.

### D-006 — Zakres przechowywania źródeł

**Status:** przyjęta  
**Decyzja:** system nie przechowuje pełnych kopii stron, HTML-a, PDF-ów ani zrzutów ekranu. Przechowuje URL, tytuł, typ źródła, datę sprawdzenia, informację o dostępności i przekierowaniach oraz krótki fragment dowodowy wymagany dla statusów `ma` i `częściowo`. Wyniki negatywne zawierają strukturalny ślad poszukiwania.

### D-007 — Hybrydowy profil narzędzia

**Status:** przyjęta  
**Decyzja:** aktywny profil narzędzia jest bezpiecznie publikowanym zestawem:

```text
data/profiles/<tool_id>/
├── profile.json
└── description.md
```

`profile.json` jest źródłem danych maszynowych: metadanych, rewizji, cech, ograniczeń, dowodów, śladów poszukiwania, faktów dodatkowych i przypadków użycia. `description.md` zawiera opis semantyczny wygenerowany przez LLM. HTML bezpiecznie renderuje Markdown, natomiast tabele i flagi generuje z JSON-a. Markdown może odwoływać się do dowodów przez stabilne identyfikatory.

### D-008 — Platformy i środowisko Python

**Status:** przyjęta  
**Decyzja:** system wspiera Python 3.11 lub nowszy na Windowsie, Linuksie i macOS. Pakiet używa `pyproject.toml`; gwarantowanym sposobem instalacji jest `venv` i `pip`, a `uv` może być opcjonalnym przyspieszeniem.

Kod nie zależy od PowerShella ani Bash, używa `pathlib` i bezpiecznych wywołań procesów. Architektura i operacje plikowe muszą być przenośne między Windows, Linux i macOS.

### D-009 — Pełny protokół dla statusu „nie ma”

**Status:** przyjęta  
**Decyzja:** ponieważ Etap 1 nie utrzymuje lokalnego korpusu, korpus ma postać logicznego rejestru oficjalnych źródeł sprawdzonych przez agentów. Status `nie ma` jest dozwolony wyłącznie po wykonaniu kompletnego i audytowalnego protokołu.

Agent źródłowy identyfikuje oficjalne domeny oraz dostępne klasy źródeł: dokumentację, strony produktowe, changelog lub release notes, cennik i licencjonowanie, dokumentację integracji oraz źródła specjalistyczne właściwe dla narzędzia.

Subagent badający cechę wykonuje:

1. wyszukiwanie nazwy kanonicznej, aliasów i synonimów ze słownika;
2. wyszukiwanie alternatywnych sformułowań wygenerowanych z definicji cechy;
3. celowane zapytania ograniczone do oficjalnych domen;
4. otwarcie i ocenę potencjalnych trafień;
5. zapis zapytań, sprawdzonych klas źródeł, odwiedzonych URL-i, daty, braków w dostępie i powodów odrzucenia trafień.

Status `nie ma` wymaga jednocześnie:

- sprawdzenia wszystkich istotnych klas źródeł;
- braku błędów uniemożliwiających istotną część badania;
- braku nierozstrzygniętych konfliktów;
- braku źródła potwierdzającego pełną albo częściową realizację;
- wartości `protocol_complete: true`;
- pozytywnej walidacji kompletności checklisty przez Python.

Niedostępność istotnego źródła, awaria narzędzia albo niepełny research prowadzi do statusu `niepewne/sporne`, nigdy do `nie ma`. Protokół nie używa sztucznego minimum liczby zapytań; wymaga pokrycia strategii i źródeł.

### D-010 — Paczki cech i współbieżność

**Status:** przyjęta  
**Decyzja:** agent prowadzący deleguje niezależne zadania w jednej warstwie subagentów. Domyślny limit wynosi czterech subagentów jednocześnie, jest konfigurowalny i nie może przekroczyć możliwości harnessu.

Zasady planowania:

- typowa paczka zawiera od dwóch do czterech powiązanych cech z tej samej grupy;
- cecha złożona, sporna albo szczególnie kosztowna otrzymuje osobne zadanie;
- każda cecha zwraca osobny rekord JSON, nawet gdy była częścią paczki;
- subagenci nie delegują zadań kolejnym subagentom;
- odkrywanie źródeł może działać równolegle według rozłącznych klas źródeł;
- po błędzie paczka jest ponawiana, a przy kolejnym problemie dzielona na pojedyncze cechy;
- agent prowadzący czeka na wszystkie obowiązkowe zadania przed scaleniem;
- przekroczenie twardego budżetu czasu lub pracy przerywa przebieg i nie publikuje niepełnego profilu;
- skill `/tool-eval-compare` nie korzysta z subagentów, ponieważ jego praca jest deterministyczna.

Konkretne limity czasu, liczby wyszukiwań i rozmiaru pracy zostaną skalibrowane po pilotażu na dwóch lub trzech narzędziach.

### D-011 — Błędy, ponawianie i wznawianie

**Status:** przyjęta  
**Decyzja:** błędy mają ustrukturyzowane kody z rodzin `CONFIG_*`, `INPUT_*`, `HARNESS_*`, `RESEARCH_*`, `VALIDATION_*`, `BUDGET_*` oraz `PUBLISH_*`. Rekord błędu zawiera etap, komunikat, pole `retryable`, opcjonalny `feature_id` i ścieżkę danych.

Zasady ponawiania:

- błąd techniczny narzędzia pozwala na maksymalnie dwa ponowienia danego zadania;
- błąd struktury lub reguł biznesowych pozwala na maksymalnie trzy rundy naprawcze LLM;
- po każdej rundzie naprawczej walidowany jest cały profil;
- błędna konfiguracja, schema, rewizja albo naruszenie bezpieczeństwa kończy przebieg natychmiast;
- przekroczenie budżetu kończy przebieg bez ponowienia;
- zadania zakończone sukcesem nie są wykonywane ponownie.

Aktywny przebieg znajduje się w `.work/runs/<run_id>/`. Można go wznowić tylko wtedy, gdy aktualny słownik, szablon, schema i polityki odpowiadają efektywnemu, zamrożonemu stanowi przebiegu. Kontrolowana akceptacja nowej cechy w punkcie kuratorskim aktualizuje efektywną rewizję i hash słownika zapisane w przebiegu; nie jest traktowana jako zewnętrzna zmiana unieważniająca wznowienie. Inna zmiana konfiguracji powoduje rozpoczęcie nowego przebiegu.

Definitywnie nieudany przebieg jest przenoszony do:

```text
.work/failed-runs/<run_id>/
├── report.json
├── run.json
├── validation-errors.json
└── artifacts/
```

Artefakty zawierają manifesty zadań, strukturalne wyniki i ostatnie niepoprawne rekordy, ale nie pełne kopie stron. Domyślna retencja wynosi 30 dni lub ostatnie 20 nieudanych przebiegów i jest konfigurowalna. Udany przebieg usuwa katalog roboczy dopiero po potwierdzeniu publikacji. Nieudany przebieg nigdy nie zmienia aktywnego profilu ani jego daty.

### D-012 — Uproszczona publikacja profilu

**Status:** przyjęta  
**Decyzja:** system działa lokalnie i nie wymaga ciągłej dostępności profilu podczas generowania nowej wersji. Nie stosuje wskaźnika `current.json`, wersjonowanych publikacji ani blokad dla równoległych czytelników.

Nowe `profile.json` i `description.md` powstają w `.work/runs/<run_id>/publish/` i są tam w pełni walidowane. Dopiero po sukcesie Python zastępuje katalog `data/profiles/<tool_id>/`. Na czas podmiany poprzedni katalog jest zachowany jako kopia techniczna w katalogu przebiegu; błąd powoduje rollback. Po potwierdzeniu poprawnego zapisu kopia techniczna jest usuwana.

Przerwanie procesu może spowodować chwilową niedostępność profilu. Następne uruchomienie wykrywa niedokończoną podmianę i przywraca poprzedni katalog. Nie utrzymujemy historii udanych profili.

### D-013 — Zewnętrzne biblioteki i samowystarczalny HTML

**Status:** przyjęta  
**Decyzja:** zewnętrzne biblioteki Python, CSS i JavaScript są dozwolone, jeżeli upraszczają generowanie treści albo warstwę prezentacji. Wynikowy HTML pozostaje jednak samowystarczalny: wszystkie wymagane zasoby są przechowywane lokalnie i osadzane w jednym pliku, bez zależności od CDN lub Internetu podczas prezentacji.

Założenia:

- szablony HTML są generowane przez bibliotekę szablonów;
- `description.md` jest renderowany przez bibliotekę Markdown;
- wynik przechodzi sanitację, a surowy HTML w Markdownzie jest domyślnie wyłączony;
- Bootstrap jest bazowym kandydatem dla układu, kart, zakładek, tooltipów i stylów tabel;
- dodatkowa biblioteka tabel lub filtrowania zostanie użyta tylko wtedy, gdy prototyp wykaże taką potrzebę;
- CSS, fonty i JavaScript bibliotek są bundlowane do artefaktu;
- wersje zależności są przypięte, a projekt ewidencjonuje ich źródła, licencje i sumy kontrolne;
- dane profili są escapowane, URL-e ograniczone do bezpiecznych protokołów, a generator przechodzi ręczną kontrolę przypadków wstrzyknięcia przed wydaniem MVP;
- podstawowa treść i tabele są dostępne bez JavaScriptu, natomiast zakładki, filtry i interakcje korzystają z JavaScriptu;
- wspierane są aktualne stabilne wersje Chrome, Edge, Firefox i Safari; stare przeglądarki i Internet Explorer są poza zakresem.

### D-014 — Minimalny stos zależności

**Status:** przyjęta  
**Decyzja:** podstawowy stos runtime Python obejmuje:

- `PyYAML` do konfiguracji YAML, używany wyłącznie przez `safe_load`;
- `jsonschema` do walidacji w standardzie JSON Schema Draft 2020-12;
- `Jinja2` do szablonów HTML z `autoescape` i `StrictUndefined`;
- `markdown-it-py` do CommonMark z wyłączonym surowym HTML-em;
- `nh3` do końcowej sanitacji wyrenderowanej treści.

Biblioteka standardowa obsługuje CLI (`argparse`), JSON, ścieżki i pliki, procesy z `shell=False`, hashe, daty, identyfikatory i logowanie. Początkowo nie dodajemy Pydantic, Click/Typer, Requests, frameworka webowego, bazy danych ani biblioteki crawlera.

Warstwa prezentacji używa dokładnie przypiętej wersji Bootstrap 5.3.x. Zbudowane pliki CSS i `bootstrap.bundle.min.js` są przechowywane jako assety projektu razem z wersją, licencją i sumami SHA-256. Nie wymagamy Node.js, npm ani CDN. Dodatkowa biblioteka tabel lub filtrowania może zostać dodana dopiero po wykazaniu potrzeby w prototypie.

Backendem budowania pakietu jest `hatchling`. Zakresy wersji bibliotek są ograniczone do kolejnej wersji głównej, natomiast dokładne wersje zostaną przypięte po ręcznym sprawdzeniu instalacji i głównych przepływów. Projekt utrzymuje `THIRD_PARTY_NOTICES.md` oraz kopie licencji bundlowanych assetów.

### D-015 — Integracja Claude Code i pakowanie skilli

**Status:** przyjęta  
**Decyzja:** Claude Code jest jedynym harnessem MVP i odpowiada za research oraz wszystkie zadania LLM. System definiuje osobnego agenta `tool-eval-orchestrator`, uruchamianego jako główny agent sesji Claude przez `claude --agent tool-eval-orchestrator`. Nie jest on subagentem, dzięki czemu może delegować równoległe zadania do `tool-eval-worker`.

Artefakty Claude Code:

```text
.claude/
├── agents/
│   ├── tool-eval-orchestrator.md
│   └── tool-eval-worker.md
└── skills/
    ├── tool-eval-research/
    ├── tool-eval-compare/
    ├── tool-eval-resume/
    ├── tool-eval-orchestration/
    ├── source-discovery/
    ├── feature-research/
    ├── profile-writing/
    ├── profile-validation/
    └── comparison/
```

Podział instrukcji:

- definicja orkiestratora określa jego rolę, narzędzia, dozwolonych workerów i nadrzędne obowiązki;
- `tool-eval-research`, `tool-eval-compare` i `tool-eval-resume` są bezpośrednio wywoływanymi skillami wejściowymi; definiują argumenty operacji i przekazują sterowanie do przepływu orkiestracyjnego;
- `tool-eval-orchestration/SKILL.md` opisuje fazy, bramki, delegowanie, kurację, retry i publikację;
- definicja workera określa izolację, sposób czytania manifestu zadania i dozwolony obszar zapisu;
- Python maszynowo egzekwuje stan i dozwoloną kolejność przejść.

Każdy skill jest pakietem i może zawierać:

```text
<skill>/
├── SKILL.md
├── references/
├── schemas/
├── examples/
└── scripts/
```

Schema lub skrypt używany wyłącznie przez jeden skill znajduje się w jego katalogu. Wspólna logika pozostaje w `src/tool_eval/` i jest wywoływana przez stabilne CLI `python -m tool_eval`. Nie duplikujemy walidatorów między skillami. JSON Schema jest źródłem prawdy, a komenda walidacyjna sprawdza wszystkie przykłady z katalogów `examples/` względem właściwych schematów; w MVP kontrola jest uruchamiana ręcznie.

MVP nie implementuje generatora adapterów, symlinków ani integracji Codex/Copilot. Instrukcje zachowują możliwie neutralną semantykę, aby późniejsza ekstrakcja adapterów nie wymagała zmiany kontraktów danych i kodu Python.

### D-016 — Model profilu i język systemu

**Status:** przyjęta  
**Decyzja:** `profile.json` ma częściowo znormalizowaną strukturę z głównymi sekcjami `schema_version`, `tool`, `research`, `sources`, `feature_results`, `additional_facts`, `use_cases` oraz `unresolved_issues`.

Źródła są rejestrowane raz na poziomie profilu i otrzymują stabilny `source_id`. Wynik każdej cechy jest samowystarczalnym rekordem zawierającym `feature_id`, `status`, `rationale`, `evidence`, `constraints`, `search_trace` i opcjonalne dane konfliktu. Dowody pozostają przy rekordzie, którego dotyczą, ale odwołują się do źródła przez `source_id`, aby nie powielać URL-i i metadanych. Schemat wyniku subagenta używa tego samego formatu rekordu cechy, dzięki czemu scalenie nie wymaga transformacji semantycznej.

Konwencje:

- wewnętrzne statusy to `has`, `partial`, `not_found` oraz `uncertain`;
- stabilne identyfikatory używają małych liter ASCII i podkreśleń;
- znaczniki czasu używają ISO 8601 i UTC;
- `schema_version` używa wersjonowania semantycznego, a rewizje słownika i szablonu pozostają liczbami całkowitymi;
- schematy ustawiają `additionalProperties: false`;
- pola opcjonalne są pomijane zamiast zapisywania jako `null`, chyba że `null` ma zdefiniowane znaczenie domenowe;
- JSON Schema sprawdza strukturę, typy i proste zależności, a walidator biznesowy reguły zależne od statusu oraz integralność referencji.

Cały implementowany system używa wyłącznie języka angielskiego: nazwy pól, enumy, identyfikatory, skille, prompty, komunikaty walidatora, dokumentacja techniczna, opis Markdown oraz interfejs HTML. Nie implementujemy lokalizacji ani plików tłumaczeń. Etykiety prezentacyjne statusów to `Has`, `Partial`, `Not found` oraz `Uncertain / disputed`.

Pole `excerpt` zachowuje dokładne brzmienie źródła. Jeśli źródło nie jest angielskie, cytat nie jest modyfikowany ani przedstawiany jako tłumaczenie; pozostałe pola opisowe pozostają angielskie. MVP preferuje anglojęzyczne źródła oficjalne.

### D-017 — Bezpieczeństwo agentów i researchu

**Status:** przyjęta  
**Decyzja:** treść wszystkich stron jest niezaufanym materiałem badawczym. Instrukcje znalezione w źródle nigdy nie zmieniają zadania agenta. Statusy cech mogą opierać się wyłącznie na publicznych, oficjalnych źródłach; inne strony mogą jedynie pomóc odnaleźć źródło oficjalne.

Worker badawczy otrzymuje wyłącznie narzędzia potrzebne do odczytania manifestu i skilla, wyszukiwania oraz otwierania stron i zapisania wyniku we własnym katalogu zadania. Nie może uruchamiać dowolnych poleceń shellowych, modyfikować konfiguracji, schematów lub aktywnych profili, publikować wyników ani delegować kolejnych agentów.

Orkiestrator może wywoływać tylko dozwolonego workera, odczytywać stan, uruchamiać określone komendy `python -m tool_eval`, prowadzić kurację oraz pętlę naprawczą. Aktywny profil zapisuje wyłącznie Python po pozytywnej walidacji.

Kontrole techniczne:

- ścieżki z manifestów są normalizowane i muszą pozostać w katalogu przebiegu;
- profil dopuszcza wyłącznie URL-e `http` i `https`, bez danych uwierzytelniających;
- agent nie pobiera ani nie wykonuje kodu znalezionego w źródłach;
- wynik workera przechodzi JSON Schema i reguły biznesowe;
- nieoczekiwane pola, ścieżki, identyfikatory i rewizje są odrzucane;
- potencjalna próba prompt injection jest ignorowana i zapisywana jako ostrzeżenie;
- sekrety, zmienne środowiskowe i lokalne dane użytkownika nie trafiają do profilu ani HTML-u;
- ręczna kontrola bezpieczeństwa MVP obejmuje złośliwy Markdown, URL-e, fragmenty źródeł i instrukcje próbujące zmienić zadanie agenta.

### D-018 — Uruchamianie i dokumentacja użytkowa MVP

**Status:** przyjęta  
**Decyzja:** MVP jest uruchamiane na żądanie w Claude Code. Operator prowadzi operacje wysokiego poziomu przez bezpośrednie wywołanie skilli wejściowych, bez warstwy `.claude/commands/` i bez ręcznego sterowania skryptami Python.

MVP udostępnia skille wywoływane przez użytkownika:

```text
/tool-eval-research <tool>
/tool-eval-compare <tool...>
/tool-eval-resume <run_id>
```

Research zatrzymuje się w jednym punkcie kuratorskim i przedstawia operatorowi wszystkich kandydatów. Operator może zaakceptować, odrzucić albo odłożyć kandydata do poczekalni.

Dokumentacja użytkowa jest obowiązkowym elementem wydania i obejmuje:

- wymagania wstępne oraz instalację na Windows, Linux i macOS;
- utworzenie środowiska Python i instalację projektu;
- uruchomienie `claude --agent tool-eval-orchestrator`;
- opis składni, argumentów, przebiegu i rezultatów każdego skilla wejściowego;
- przykładową sesję badania, kuracji, wznowienia i porównania;
- opis katalogów profili, porównań, aktywnych i nieudanych przebiegów;
- interpretację statusów, ograniczeń, świeżości i ostrzeżeń;
- rozwiązywanie typowych błędów oraz sposób bezpiecznego wznowienia.

### D-019 — Pionowe przyrosty implementacji

**Status:** przyjęta  
**Decyzja:** MVP powstaje w pięciu przyrostach dostarczających kolejno: fundament projektu, pełny research narzędzia, porównanie i samowystarczalny HTML, obsługę operacyjną z dokumentacją oraz ręczną akceptację MVP. Każdy przyrost kończy się działającym rezultatem możliwym do ręcznego zweryfikowania. Szczegółowy backlog i bramki znajdują się w sekcji 5.

### Ustalony podział formatów

- YAML — konfiguracja edytowana ręcznie;
- JSON — profile, manifesty, zadania, wyniki subagentów, kandydaci i raporty błędów;
- JSON Schema — walidacja danych generowanych;
- Markdown — skille, agenci, dokumentacja i opis semantyczny profilu;
- HTML — samowystarczalny artefakt wynikowy.

## 3. Architektura docelowa MVP

### 3.1 Przepływ odpowiedzialności

```text
Direct Claude skill invocation
        │
        ▼
tool-eval-orchestrator (main Claude session agent)
        │
        ├── loads workflow and domain skills
        ├── calls deterministic Python CLI
        └── delegates isolated research tasks
                    │
                    ▼
            tool-eval-worker subagents
                    │
                    └── web research + validated JSON results
        │
        ▼
Python: validate → merge → calculate → render → publish
        │
        ├── data/profiles/<tool_id>/
        └── outputs/comparisons/<comparison_id>.html
```

Claude odpowiada za research, interpretację źródeł, klasyfikację semantyczną, wykrywanie konfliktów i tworzenie angielskiej treści. Python nie komunikuje się z modelem i nie prowadzi researchu. Egzekwuje stan, kontrakty, reguły biznesowe, arytmetykę, sanitację oraz zapis danych.

### 3.2 Komponenty

#### `tool-eval-orchestrator`

Główny agent sesji uruchomionej przez `claude --agent tool-eval-orchestrator`. Obsługuje bezpośrednio wywołany skill wejściowy, ładuje skill orkiestracyjny, wywołuje CLI Python, uruchamia do czterech workerów, prowadzi punkt kuratorski oraz pętlę naprawczą. Nie zapisuje bezpośrednio aktywnych profili i nie oblicza flag porównania.

#### `tool-eval-worker`

Generyczny subagent wykonujący jedno zadanie z `task.json`. Specjalizację określają `task_type` oraz wskazany skill. Worker czyta wyłącznie jawne wejścia, wykonuje research narzędziami Claude i zapisuje wynik we własnym katalogu. Nie publikuje, nie scala, nie zmienia konfiguracji i nie deleguje dalej.

#### Skille Claude

- `tool-eval-orchestration` — fazy, bramki, retry, resume, kuracja i publikacja;
- `source-discovery` — oficjalne domeny, klasy źródeł i rejestr źródeł;
- `feature-research` — statusy, dowody, ograniczenia, konflikty i protokół D-009;
- `profile-writing` — additional facts, use cases i `description.md`;
- `profile-validation` — interpretacja raportów walidatora i naprawa danych;
- `comparison` — sposób uruchomienia deterministycznego porównania i interpretacja wyniku.

#### Pakiet Python `tool_eval`

- ładuje i zamraża konfigurację oraz rewizje;
- tworzy przebiegi, manifesty i zadania;
- waliduje JSON Schema oraz reguły biznesowe;
- scala wyniki workerów i kontroluje kompletność;
- zarządza kandydatami i rewizjami;
- publikuje i przywraca profile;
- oblicza świeżość oraz flagi porównania;
- renderuje Markdown, sanitizuje treść i generuje HTML;
- obsługuje retry, resume, failed runs, retencję i recovery.

### 3.3 Struktura repozytorium

```text
tool-eval/
├── .claude/
│   ├── agents/
│   │   ├── tool-eval-orchestrator.md
│   │   └── tool-eval-worker.md
│   └── skills/
│       ├── tool-eval-research/
│       ├── tool-eval-compare/
│       ├── tool-eval-resume/
│       ├── tool-eval-orchestration/
│       ├── source-discovery/
│       ├── feature-research/
│       ├── profile-writing/
│       ├── profile-validation/
│       └── comparison/
├── config/
│   ├── feature-taxonomy.yaml
│   ├── source-policies.yaml
│   ├── profile-sections.yaml
│   ├── freshness.yaml
│   ├── runtime.yaml
│   └── presentation.yaml
├── src/tool_eval/
│   ├── __main__.py
│   ├── cli.py
│   ├── errors.py
│   ├── config/
│   ├── runs/
│   ├── validation/
│   ├── research/
│   ├── profiles/
│   ├── comparison/
│   └── reporting/
│       ├── templates/
│       └── assets/
├── data/
│   ├── profiles/<tool_id>/
│   │   ├── profile.json
│   │   └── description.md
│   └── feature-candidates/
│       ├── pending.json
│       └── rejected.json
├── outputs/comparisons/
├── .work/
│   ├── runs/
│   └── failed-runs/
├── docs/
│   ├── dokument_wymagan_system_porownywania_narzedzi_ai_v2.md
│   ├── plan_implementacji_v1.md
│   └── user-guide.md
├── pyproject.toml
├── THIRD_PARTY_NOTICES.md
├── README.md
└── .gitignore
```

Każdy katalog skilla może zawierać `SKILL.md`, `references/`, `schemas/`, `examples/` i `scripts/`. Wspólny kod Python nie jest kopiowany do skilli. `.work/` jest ignorowany przez Git. Profile, konfiguracja, skille i zaakceptowane zmiany słownika są trwałymi elementami repozytorium.

### 3.4 Artefakty przebiegu

```text
.work/runs/<run_id>/
├── run.json
├── frozen-config/
├── tasks/<task_id>/
│   ├── task.json
│   ├── input.json
│   ├── result.json
│   └── validation.json
├── merged/
│   ├── sources.json
│   ├── feature-results.json
│   ├── candidates.json
│   └── unresolved-issues.json
├── repairs/<round_number>/
├── publish/
│   ├── profile.json
│   └── description.md
└── validation-errors.json
```

`run.json` zawiera identyfikatory, operację, stan, czasy, początkowe i efektywne rewizje oraz hashe konfiguracji, liczniki retry, listę obowiązkowych zadań, budżety i historię przejść. Kontrolowana zmiana słownika po akceptacji kandydata jest zapisywana jako jawne przejście rewizji. Python jest jedynym komponentem zmieniającym stan manifestu głównego.

### 3.5 Skille użytkownika i CLI wewnętrzne

Sesja użytkownika:

```text
claude --agent tool-eval-orchestrator
/tool-eval-research <tool_name>
/tool-eval-compare <tool_id> <tool_id> [<tool_id>...]
/tool-eval-resume <run_id>
```

Minimalny wewnętrzny interfejs Python:

```text
python -m tool_eval config validate
python -m tool_eval run init|status|resume-check|fail
python -m tool_eval research create-source-task
python -m tool_eval research accept-sources
python -m tool_eval research create-feature-tasks
python -m tool_eval research validate-task
python -m tool_eval research merge
python -m tool_eval research curate-candidates
python -m tool_eval research prepare-repair
python -m tool_eval research build-profile
python -m tool_eval profile validate|publish|list
python -m tool_eval compare build
python -m tool_eval work cleanup|recover
```

Każda wewnętrzna komenda CLI zapisuje logi na `stderr`, a na `stdout` zwraca małą kopertę JSON z `status`, `code`, `run_id`, `next_action`, `artifacts` i opcjonalnymi `errors`. Duże dane zawsze pozostają w plikach zgodnych ze schematem.

### 3.6 Przepływ skilla `/tool-eval-research`

1. Walidacja konfiguracji i utworzenie przebiegu.
2. Zamrożenie rewizji słownika, szablonu, schematów i polityk.
3. Discovery znanych i nowych oficjalnych źródeł.
4. Walidacja logicznego rejestru źródeł.
5. Utworzenie paczek po 2–4 cechy i uruchomienie workerów do limitu czterech.
6. Walidacja każdego wyniku; techniczny retry lub podział błędnej paczki.
7. Deterministyczne scalenie i kontrola dokładnie jednego wyniku każdej cechy.
8. Ekstrakcja faktów, przypadków użycia i kandydatów.
9. Jeden interaktywny punkt kuratorski: accept, reject lub defer.
10. Dla zaakceptowanych kandydatów: walidacja definicji, aktualizacja słownika przez Python, zwiększenie rewizji, zapis kontrolowanego przejścia w przebiegu i oznaczenie pozostałych profili jako `requires_research`.
11. Utworzenie i wykonanie zadań badawczych dla zaakceptowanych cech bieżącego narzędzia oraz ponowne scalenie wyników.
12. Kontrola dokładnie jednego wyniku każdej cechy z efektywnej rewizji słownika.
13. Złożenie `profile.json` i `description.md`.
14. JSON Schema, reguły biznesowe i maksymalnie trzy rundy naprawcze.
15. Walidacja stagingu, podmiana katalogu profilu i raport końcowy.

Najważniejsze bramki: brak zaakceptowanego rejestru źródeł blokuje research cech; brak wyniku workera blokuje scalenie; `not_found` wymaga D-009; kandydaci muszą otrzymać decyzję; zaakceptowana cecha musi zostać zbadana dla bieżącego narzędzia przed publikacją; niepoprawny lub niekompletny profil nie może zostać opublikowany.

### 3.7 Przepływ skilla `/tool-eval-compare`

1. Rozpoznanie narzędzi i skopiowanie aktywnych profili do katalogu przebiegu porównania.
2. Walidacja profili, rewizji i dat.
3. Dopuszczenie profili `requires_research` z ostrzeżeniem; niezbadane komórki są wyłączone z flag.
4. Deterministyczne obliczenie świeżości, rozjazdu dat i flag.
5. Złożenie modelu widoku.
6. Renderowanie i sanitacja `description.md`.
7. Renderowanie szablonu Jinja2 z osadzonym Bootstrapem, CSS i JavaScript.
8. Publikacja pojedynczego pliku w `outputs/comparisons/`.

Porównanie nie uruchamia researchu ani subagentów. Brak profilu jest błędem dla wskazanego narzędzia, natomiast starsza rewizja lub data generuje ostrzeżenie.

## 4. Zakres MVP i odroczenia

### 4.1 Zakres obowiązkowy

- Claude Code jako jedyny harness;
- research, compare i resume uruchamiane przez bezpośrednio wywoływane skille Claude;
- 20–30 cech początkowych;
- pełny research, kandydaci i kuracja;
- profile JSON + Markdown;
- deterministyczne porównanie i samowystarczalny HTML;
- failed runs, retry, resume, rollback i recovery;
- angielski kontrakt danych, instrukcje i prezentacja;
- instrukcja instalacji, skilli wejściowych i troubleshooting;
- ręczna akceptacja względem 15 kryteriów Etapu 1.

### 4.2 Poza MVP

- Codex CLI, GitHub Copilot CLI i generator adapterów;
- bezpośrednie API LLM;
- crawler, lokalny korpus, archiwum stron, BM25, embeddingi i baza wektorowa;
- aplikacja webowa, hosting, backend i telemetryka;
- historia profili i źródeł;
- Node.js jako obowiązkowa zależność;
- i18n oraz języki inne niż angielski;
- eksport PDF;
- Sekcja B i benchmarki skuteczności.

### 4.3 Elementy kalibrowane podczas pilotażu

Nie są decyzjami blokującymi rozpoczęcie implementacji: dokładne limity czasu i pracy, ostateczny rozmiar paczek dla trudnych cech, potrzeba dodatkowej biblioteki tabel oraz dokładne wersje zależności w przyjętych zakresach.

## 5. Plan prac

### Przyrost 1 — fundament projektu

**Cel:** instalowalny szkielet, kontrakty i integracja Claude bez pełnego researchu.

1. Utworzyć `pyproject.toml`, `src/tool_eval`, `python -m tool_eval` i wspólną kopertę odpowiedzi CLI.
2. Utworzyć katalogi runtime i reguły odnajdywania root projektu.
3. Dodać YAML-e konfiguracji, rewizje i walidację przez `safe_load`.
4. Przygotować pod nadzorem kuratora początkowy słownik 20–30 cech.
5. Zdefiniować bazowe schematy run, task, source i feature result.
6. Zaimplementować model błędów i bezpieczne ścieżki.
7. Utworzyć agenta orkiestrującego, workera i bazowy skill orkiestracyjny.
8. Utworzyć szkielety trzech bezpośrednio wywoływanych skilli Claude.

**Równolegle:** konfiguracja, model błędów i struktura katalogów po utworzeniu pakietu; słownik oraz schematy po ustaleniu formatu YAML.

**Bramka:** pakiet instaluje się na Pythonie 3.11+, konfiguracja jest poprawna, Claude rozpoznaje agentów i skille wejściowe, a żaden element nie wymaga klucza API.

### Przyrost 2 — pełny research narzędzia

**Cel:** kompletna, równoległa i wznawialna operacja dla całego słownika.

1. Uzupełnić pełny model profilu i referencje między rekordami.
2. Zaimplementować planner paczek oraz fale maksymalnie czterech workerów.
3. Zaimplementować pełny protokół D-009, dowody, ograniczenia i konflikty.
4. Dodać additional facts, documented/inferred use cases i pełne `description.md`.
5. Dodać kandydatów, jedną bramkę kuratorską, waiting room i kontrolowane rewizje; zaakceptowaną cechę dodać do słownika, zbadać dla bieżącego narzędzia i oznaczyć pozostałe profile jako `requires_research`.
6. Scalać deterministycznie i sprawdzać kompletność wszystkich cech.
7. Dodać dwa retry techniczne, podział paczki oraz trzy rundy naprawcze.
8. Dodać `.work/failed-runs`, retencję i skill `/tool-eval-resume`.
9. Dodać staging, rollback i bezpieczne zastąpienie aktywnego profilu.

**Równolegle:** protokół negatywny, ograniczenia i kandydaci po gotowym plannerze; failed runs i resume po ustaleniu maszyny stanów.

**Bramka:** cały słownik ma dokładnie po jednym wyniku, `not_found` nie przechodzi bez protokołu, kandydaci są rozstrzygnięci, a nieudany przebieg nie zmienia profilu.

### Przyrost 3 — porównanie i samowystarczalny HTML

**Cel:** deterministyczny raport kilku profili działający offline.

1. Wczytywać i walidować profile, daty oraz rewizje.
2. Obliczać świeżość, rozjazd dat i flagi zgodnie z wymaganiami.
3. Wyłączać niekompletne komórki z flag i pokazywać ostrzeżenia.
4. Renderować CommonMark, rozwijać odwołania do dowodów i sanitizować przez `nh3`.
5. Przygotować Jinja2 z `StrictUndefined` i autoescape.
6. Osadzić przypięty Bootstrap, licencję, CSS i mały skrypt vanilla JS.
7. Dodać karty, filtry, profile oraz klasyczne tooltipy uruchamiane po najechaniu kursorem.
8. Dodać ręczne przypadki bezpieczeństwa i skill `/tool-eval-compare`.

**Równolegle:** obliczenia flag, pipeline Markdown i prototyp szablonu po ustaleniu modelu widoku.

**Bramka:** cztery profile tworzą pojedynczy angielski HTML działający offline, z deterministycznymi flagami, datami, ostrzeżeniami, profilami i bez wykonywania danych jako kodu.

### Przyrost 4 — obsługa operacyjna i dokumentacja

**Cel:** MVP możliwe do samodzielnego użycia przez osobę spoza implementacji.

1. Dopracować komunikaty sukcesu, błędów i następnych kroków.
2. Dodać konfigurowalne budżety, cleanup i retencję failed runs.
3. Dodać recovery niedokończonej publikacji.
4. Napisać angielską instrukcję instalacji dla trzech systemów.
5. Opisać research, compare i resume: składnię, przebieg, wyniki i błędy.
6. Dodać przykładowe sesje kuracji, failed run, resume i porównania.
7. Dodać troubleshooting i jawną listę ograniczeń MVP.

**Równolegle:** mechanizmy operacyjne oraz dokumentacja po ustabilizowaniu skilli wejściowych.

**Bramka:** nowy użytkownik korzystający wyłącznie z dokumentacji instaluje projekt, uruchamia orkiestratora, bada narzędzie, wznawia przebieg i generuje porównanie.

### Przyrost 5 — ręczna akceptacja MVP

**Cel:** potwierdzenie pełnego rozwiązania w rzeczywistych sesjach Claude Code.

1. Przygotować checklistę 15 kryteriów z wynikiem pass/fail.
2. Zbadać cztery rzeczywiste narzędzia pełnym słownikiem.
3. Ponownie zbadać jedno narzędzie, używając znanych i nowych źródeł.
4. Wykonać kontrolowaną porażkę i sprawdzić zachowanie starego profilu.
5. Zaakceptować, odrzucić i odłożyć kandydatów; sprawdzić rewizje.
6. Wznowić zgodny przebieg i odrzucić wznowienie po zmianie rewizji.
7. Wygenerować porównanie czterech profili i otworzyć je offline.
8. Sprawdzić złośliwy Markdown, URL i prompt injection.
9. Zweryfikować instrukcję z osobą nieuczestniczącą w implementacji.
10. Sporządzić raport akceptacyjny i listę prac po MVP.

**Bramka:** wszystkie 15 kryteriów ma wynik `pass`, nie ma publikacji niewalidowanego profilu, HTML działa offline, a dokumentacja prowadzi przez cały przepływ. Kryterium może przestać blokować wydanie wyłącznie po wcześniejszym zatwierdzeniu zmiany dokumentu wymagań; `accepted limitation` nie jest wynikiem zaliczającym.

### Zależności między przyrostami

```text
P1 Fundament
    ↓
P2 Full research
    ├──────────────┐
    ↓              ↓
P3 Compare/HTML    P4 Operations/docs
    └───────┬──────┘
            ↓
P5 Manual acceptance
```

## 6. Ryzyka i działania ograniczające

| ID | Ryzyko | Prawdopodobieństwo / wpływ | Działania ograniczające | Ryzyko rezydualne |
|---|---|---|---|---|
| R-01 | Niedeterministyczne odpowiedzi Claude dają różne statusy. | wysokie / wysokie | Ścisłe skille, schematy, reguły biznesowe, pełna walidacja i Python jako jedyny merger/publisher. | Interpretacja dowodów pozostaje zależna od modelu; sporne wyniki mają `uncertain`. |
| R-02 | Research bez lokalnego korpusu błędnie daje `not_found`. | średnie / wysokie | Pełny protokół D-009, logiczny rejestr źródeł, ślad zapytań i `uncertain` przy luce. | Nie da się dowieść pokrycia całego Internetu. |
| R-03 | Oficjalne strony są niedostępne lub blokują narzędzia Claude. | średnie / średnie | Retry techniczny, alternatywne oficjalne źródła, rejestr dostępności i `uncertain`. | Część cech może pozostać nierozstrzygnięta. |
| R-04 | Brak kopii stron utrudnia odtworzenie decyzji. | wysokie / średnie | URL, tytuł, typ, data i krótki wierny excerpt. | Zmiana strony uniemożliwi pełną reprodukcję; kompromis jest świadomy. |
| R-05 | Prompt injection wpływa na workera. | średnie / wysokie | Niezaufana treść, ograniczone narzędzia, brak shella i wykonywania kodu, bramki Python. | Ochrona instrukcyjna nie jest absolutna. |
| R-06 | Workery zwracają konflikty lub zapisują poza zadaniem. | średnie / wysokie | Izolowane katalogi, stabilne ID, jedna warstwa delegowania, walidacja ścieżek i jeden zapisujący. | Konflikty semantyczne mogą wymagać operatora. |
| R-07 | Zmiana słownika lub schematu miesza niezgodne dane. | średnie / wysokie | Zamrożone rewizje, `requires_research`, kontrola resume i wyłączenie niezbadanych komórek z flag. | Zmiana taksonomii wymusza kosztowny re-research. |
| R-08 | Awaria publikacji uszkadza aktywny profil. | niskie / wysokie | Staging, walidacja, kopia techniczna, rollback i recovery. | Profil może być chwilowo niedostępny. |
| R-09 | Dane profilu wykonują kod w HTML-u. | średnie / wysokie | Jinja2 autoescape, Markdown bez raw HTML, `nh3`, bezpieczne URL-e i ręczne przypadki adversarial. | Aktualizacja bibliotek wymaga ponownej kontroli. |
| R-10 | Biblioteki UI tworzą podatność lub problem licencyjny. | średnie / średnie | Przypięte wersje, lokalne assety, SHA-256, licencje i brak CDN. | Aktualizacje są ręczne. |
| R-11 | Kontekst, czas lub limit workerów przerywa research. | wysokie / średnie | Paczki 2–4, maksymalnie cztery workery, podział paczki, resume i budżety. | Złożone narzędzie może wymagać kilku sesji. |
| R-12 | Trzy systemy nie zachowują się identycznie. | średnie / średnie | `pathlib`, `shell=False`, brak skryptów shellowych i ręczna weryfikacja na każdym OS. | Różnice filesystemu mogą ujawnić się u użytkownika. |
| R-13 | Claude-only utrudnia późniejszą przenośność. | wysokie / średnie | Neutralne kontrakty i Python; szczegóły Claude wyłącznie w `.claude/`. | Inne harnessy będą wymagały nowych instrukcji delegowania. |
| R-14 | Uruchamianie na żądanie nie zapewnia samoistnej świeżości danych. | wysokie / średnie | Widoczne daty, progi świeżości, ostrzeżenia i instrukcja okresowego researchu. | Profil pozostaje stary do reakcji operatora. |

## 7. Macierz pokrycia kryteriów akceptacji Etapu 1

| # | Kryterium | Mechanizm | Przyrost | Weryfikacja MVP |
|---:|---|---|---|---|
| 1 | Research tworzy profil nowego narzędzia. | Skill Claude, orchestrator, worker, profile builder i publisher. | P2 | Ręczne utworzenie obu plików profilu. |
| 2 | Re-research używa znanych i szuka nowych źródeł. | Odczyt `sources`, source discovery i nowy ślad zapytań. | P2 | Ponowne badanie jednego narzędzia. |
| 3 | Każda cecha ma jeden poprawny wynik. | Zamrożony słownik, unikalny `feature_id`, completeness validator. | P1–P2 | Brak, duplikat i obce ID są odrzucane. |
| 4 | Wynik ma dowód albo protokół. | `evidence`, `source_id`, `search_trace` i D-009. | P2 | Scenariusze wszystkich czterech statusów. |
| 5 | Ograniczenia są strukturalne, źródłowe i widoczne. | `constraints`, evidence refs i komponent HTML. | P2–P3 | Ograniczenie jest widoczne wraz ze źródłem. |
| 6 | Oficjalna integracja może dać `has`; społecznościowa nie. | Source policy, `official`, integration rules. | P1–P2 | Dwa ręczne scenariusze integracji. |
| 7 | Kandydaci są kuratorowani razem lub odłożeni. | Jedna bramka, accept/reject/defer, waiting room oraz obowiązkowy research zaakceptowanej cechy dla bieżącego narzędzia. | P2 | Kilku kandydatów w jednym punkcie; zaakceptowana cecha ma wynik przed publikacją profilu. |
| 8 | Zmiana słownika lub szablonu oznacza stare profile. | Kontrolowane przejście rewizji, `requires_research` i kontrola resume/compare. | P1–P3 | Akceptacja cechy zwiększa rewizję, aktualizuje bieżący przebieg i oznacza pozostałe profile. |
| 9 | Walidator podaje błędy i najwyżej trzy naprawy. | Ustrukturyzowane błędy i licznik rund. | P1–P2 | Czwarta naprawa jest niedozwolona. |
| 10 | Nieudany research nie zmienia profilu ani daty. | Staging, rollback, recovery i failed run. | P2, P4 | Kontrolowana awaria po zbudowaniu stagingu. |
| 11 | Compare tworzy samowystarczalny HTML z kartami i profilami. | Comparison builder, Jinja2, Markdown i bundlowany Bootstrap. | P3 | Plik czterech profili działa offline. |
| 12 | Flagi są deterministyczne, niekompletne cechy wyłączone. | Czyste funkcje Python i kontrola kompletności. | P3 | Powtórne generowanie daje te same flagi. |
| 13 | HTML pokazuje daty, wiek i rozjazd. | UTC metadata, freshness config i warnings. | P3 | Profile z kontrolowanymi datami. |
| 14 | Profil ma opis, fakty i oba typy use cases. | `description.md`, `additional_facts`, documented/inferred use cases. | P2–P3 | Kontrola profilu pilotażowego i HTML. |
| 15 | Strona nie steruje agentem ani nie wykonuje kodu. | Ograniczony worker, untrusted-content policy, sanitacja i safe URLs. | P1–P3 | Prompt injection, raw HTML, script i `javascript:`. |

## 8. Warunek rozpoczęcia i zakończenia implementacji

Nie ma otwartych decyzji blokujących rozpoczęcie Przyrostu 1. Elementy kalibrowane w pilotażu mają wartości domyślne i nie powinny prowadzić do projektowania rozszerzeń przed pojawieniem się rzeczywistej potrzeby.

MVP jest ukończone po przejściu bramki Przyrostu 5, uzyskaniu wyniku `pass` dla wszystkich 15 kryteriów, zamknięciu wszystkich błędów blokujących oraz przygotowaniu raportu `MVP accepted`. Odstępstwo jest dopuszczalne wyłącznie po wcześniejszym zatwierdzeniu i zapisaniu zmiany dokumentu wymagań. Niezrealizowane elementy spoza MVP trafiają do osobnego backlogu i nie są dopisywane do bieżącego przyrostu bez jawnej zmiany zakresu.
