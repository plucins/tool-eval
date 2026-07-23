# Dokument wymagań — System porównywania narzędzi AI do kodowania

**Wersja:** 2.1  
**Status:** zatwierdzona baza wymagań MVP  
**Data:** 13 lipca 2026  
**Odbiorcy:** zespół i klienci wewnętrzni

---

## Spis treści

1. [Cel dokumentu](#1-cel-dokumentu)
2. [Streszczenie](#2-streszczenie)
3. [Problem i cele](#3-problem-i-cele)
4. [Zasady nadrzędne](#4-zasady-nadrzędne)
5. [Zakres i etapy](#5-zakres-i-etapy)
6. [Odbiorcy i HTML](#6-odbiorcy-i-html)
7. [Obiekty i cykle życia](#7-obiekty-i-cykle-życia)
8. [Słownik cech](#8-słownik-cech)
9. [Statusy](#9-statusy)
10. [Ograniczenia i integracje](#10-ograniczenia-i-integracje)
11. [Źródła i polityki](#11-źródła-i-polityki)
12. [Pełny protokół poszukiwania](#12-pełny-protokół-poszukiwania)
13. [Klatka LLM](#13-klatka-llm)
14. [Profil semantyczny](#14-profil-semantyczny)
15. [Skill `/tool-eval-research`](#15-skill-tool-eval-research)
16. [Pełny przepływ działania mechanizmu](#16-pełny-przepływ-działania-mechanizmu)
17. [Walidacja i zapis](#17-walidacja-i-zapis)
18. [Porównanie i flagi](#18-porównanie-i-flagi)
19. [Świeżość](#19-świeżość)
20. [Sekcja B — Etap 2](#20-sekcja-b--etap-2)
21. [Role techniczne](#21-role-techniczne)
22. [Konfiguracja](#22-konfiguracja)
23. [Wymagania niefunkcjonalne](#23-wymagania-niefunkcjonalne)
24. [Kryteria akceptacji Etapu 1](#24-kryteria-akceptacji-etapu-1)
25. [Plan implementacji](#25-plan-implementacji)
26. [Otwarte szczegóły implementacyjne](#26-otwarte-szczegóły-implementacyjne)
27. [Przyjęte kompromisy](#27-przyjęte-kompromisy)

## 1. Cel dokumentu

Dokument opisuje system badający, opisujący i porównujący narzędzia AI do kodowania na żądanie operatora. Definiuje zakres produktu, model danych, reguły wnioskowania, rolę LLM i skryptów, przepływy operatora, walidację oraz postać wyników.

Uzasadnienia kluczowych decyzji zostały zachowane celowo. Mają chronić projekt przed późniejszymi uproszczeniami, które obniżałyby wiarygodność porównania.

## 2. Streszczenie

System bada narzędzia takie jak GitHub Copilot, Cursor, Claude Code, Devin, Kiro, OpenCode, Antigravity i kolejne produkty. Korzysta z publicznych dokumentacji, changelogów, stron produktowych, cenników, katalogów integracji i — w drugim etapie — źródeł benchmarków.

Tworzy:

1. **Profil narzędzia** — fakty, dowody, ograniczenia, informacje techniczne, przypadki użycia i opis semantyczny.
2. **Porównanie zdolności** — tabele podzielone na karty grup cech, z deterministycznymi flagami.
3. **Porównanie skuteczności** — w drugim etapie, benchmarki pogrupowane według podmiotu dostarczającego wyniki.

System nie jest aplikacją webową 24/7. Jest zestawem agentów, skilli, konfiguracji i skryptów uruchamianych na żądanie operatora. Wynikiem jest samowystarczalny HTML otwierany bez serwera.

Filozofią systemu jest transparentność: wynik pokazuje źródła, warunki dostępności, datę badania, wiek danych i informacje sporne.

## 3. Problem i cele

System wspiera:

1. **Enablement zespołu** — poznanie możliwości, mechanizmów i przypadków użycia.
2. **Klientów wewnętrznych** — udostępnianie profili i porównań bez ponownego ręcznego researchu.
3. **Monitoring rynku** — utrzymywanie aktualnego obrazu możliwości produktów.

Centralnym problemem jest różne nazewnictwo podobnych funkcji. Rozwiązaniem jest kanoniczny słownik cech, na który LLM mapuje język vendorów.

Drugim problemem jest to, że dokumentacja opisuje głównie możliwości, a nie ich brak. System stosuje więc pełny protokół poszukiwania, po którego ukończeniu może operacyjnie stwierdzić, że funkcji nie ma.

## 4. Zasady nadrzędne

### 4.1 Profil jest źródłem, tabela pochodną

Najpierw powstaje kompletny profil pojedynczego narzędzia. Dopiero potem skrypt zestawia wybrane profile. LLM nie generuje tabeli bezpośrednio z pamięci.

### 4.2 Zdolności są oddzielone od skuteczności

- **Sekcja A — Mapa zdolności:** co narzędzie posiada i na jakich warunkach.
- **Sekcja B — Skuteczność:** jak narzędzie wypada w benchmarkach.

Dokumentacja vendora może potwierdzać funkcję, ale nie jej jakość. Oceny skuteczności nie przechodzą do Sekcji A.

### 4.3 LLM prowadzi research, skrypt kontroluje

LLM, działający przez agenta i narzędzia internetowe harnessu, prowadzi cały research: odkrywa źródła, otwiera i ocenia treści, wyszukuje informacje po znaczeniu, mapuje je na cechy, analizuje konflikty oraz tworzy opis. Skrypty Python utrzymują stan przebiegu, przygotowują kontrakty, walidują wyniki, kontrolują kompletność śladu poszukiwania, zarządzają rewizjami, liczą flagi, generują HTML i publikują poprawne artefakty.

### 4.4 Tryb „zawsze as-is”

Przechowywany jest tylko aktualny profil narzędzia. Udane ponowne badanie nadpisuje poprzedni stan. Nie utrzymujemy historii profili ani pełnej odtwarzalności starych wyników.

Wygenerowany HTML pozostaje zamrożony. Ryzyko braku pełnej reprodukcji jest świadomie zaakceptowane; granicę odpowiedzialności wyznacza data badania.

### 4.5 Ograniczenie nie odbiera statusu „ma”

Jeżeli funkcja istnieje w oficjalnie wspieranym wariancie produktu, otrzymuje status „ma”, nawet gdy działa tylko w określonym planie, środowisku, modelu, regionie, wersji beta lub przez oficjalną integrację. Warunki są zapisane jako ograniczenia.

## 5. Zakres i etapy

### 5.1 Narzędzia

Zakres obejmuje asystentów i agentów AI do kodowania. Lista jest otwarta. Dodanie narzędzia nie może wymagać zmiany generatora ani kodu istniejących profili.

CLI, edytor, plugin IDE i web są cechami formy dostępu, nie osobnymi kategoriami produktu.

### 5.2 Etap 1 — profile i mapa zdolności

Pierwsza implementacja obejmuje:

- słownik cech i poczekalnię;
- onboarding i ponowne badanie źródeł;
- pełny protokół poszukiwania;
- statusy, dowody i ograniczenia;
- profile oraz opis semantyczny;
- walidację i pętlę naprawczą;
- flagi arytmetyczne;
- porównanie Sekcji A i HTML.

### 5.3 Etap 2 — benchmarki

Drugi etap obejmuje:

- źródła i model benchmarków;
- ocenę porównywalności;
- zakładki według dostawcy wyników;
- rozróżnienie pomiarów niezależnych i raportowanych przez vendorów;
- integrację Sekcji B z HTML-em.

Sekcja B jest opisana w tym dokumencie, ale nie blokuje Etapu 1.

### 5.4 Poza zakresem

Historia zmian funkcji, publiczna aplikacja webowa, widok sprzedażowy dla klienta zewnętrznego, sentyment, opinie i wybór „najlepszego” narzędzia.

## 6. Odbiorcy i HTML

Pierwszy artefakt jest przeznaczony dla zespołu i klientów wewnętrznych.

### Widok porównawczy

- karta dla każdej grupy cech;
- cechy w wierszach, narzędzia w kolumnach;
- statusy, ograniczenia i flagi;
- filtry;
- daty i ostrzeżenia o świeżości;
- oznaczenia profili wymagających badania;
- przejście do profilu narzędzia.

### Widok pojedynczego narzędzia

- charakterystyka i formy dostępu;
- szczegółowa mapa zdolności;
- wewnętrzne narzędzia i mechanizmy;
- przepływy pracy i przypadki użycia;
- integracje, bezpieczeństwo i ograniczenia;
- informacje sporne;
- źródła i data badania.

Tooltipy pokazujące szczegóły działają klasycznie po najechaniu kursorem.

## 7. Obiekty i cykle życia

### Profil

Aktualne źródło prawdy o narzędziu. Zawiera wyniki cech, dowody, ograniczenia, fakty dodatkowe, przypadki użycia, opis LLM i datę. Nieudane badanie go nie zastępuje.

### Porównanie

Powstaje z aktualnych profili. Ma własną datę oraz datę badania każdego narzędzia. Jest zamrożonym HTML-em.

### Słownik cech

Kanoniczna lista cech ma bieżący numer rewizji służący do wykrywania profili wymagających badania. Nie wymaga to przechowywania historii słownika.

### Szablon profilu

Edytowalna lista sekcji opisu ma własną rewizję. Zmiana wymaganej sekcji oznacza starsze profile jako wymagające ponownego badania.

### Poczekalnia

Przechowuje zdolności spoza słownika. Operator może je zaakceptować, odrzucić albo odłożyć.

## 8. Słownik cech

Słownik ma strukturę „grupa → cecha”. Każda cecha zawiera:

- stabilny identyfikator feature_id;
- nazwę, grupę i definicję;
- kryteria „ma” i „częściowo”;
- wykluczenia;
- aliasy i synonimy;
- pytanie badawcze dla LLM.

Pierwszy słownik powstaje inkluzywnie pod nadzorem człowieka i obejmuje każdą wyraźną zdolność przyjętą przez kuratora, także singleton. Kandydat ma definicję, grupę, dowody, źródła i roboczą sugestię istotności. Sugestia służy wyłącznie kuracji.

Nie istnieje próg „dojrzałości słownika”. Każde badanie lekko wykrywa nowe zdolności. Kandydaci są przedstawiani razem w jednym punkcie kuratorskim. Operator może ich zaakceptować, odrzucić albo odłożyć do poczekalni.

Akceptacja cechy zwiększa rewizję słownika. Starsze profile otrzymują stan requires_research. Brak pola nowej cechy nie oznacza „nie ma” i nie uczestniczy w flagach.

## 9. Statusy

### „ma”

Istnieje dowód realizacji pełnej definicji. Wymagany jest cytat i źródło.

### „częściowo”

Narzędzie realizuje część definicji. Wymagane są dowód i opis zakresu. Status nie służy oznaczaniu ograniczonego planu, platformy ani bety.

### „nie ma”

Pełny protokół został ukończony i nie znaleziono publicznego potwierdzenia funkcji.

> „Nie ma” oznacza, że na dzień badania pełny protokół nie znalazł potwierdzenia w zbadanych publicznych źródłach. Nie jest twierdzeniem o funkcjach niepublicznych lub nieudokumentowanych.

Dowodem jest ślad poszukiwania, nie cytat o nieobecności.

### „niepewne/sporne”

Badanie było niewystarczające, definicja niejednoznaczna albo źródła są sprzeczne. Wymagana jest przyczyna i zachowanie dowodów konfliktu.

### „wymaga badania”

Stan techniczny profilu, nie status merytoryczny cechy.

## 10. Ograniczenia i integracje

Funkcja dostępna w dowolnym oficjalnie wspieranym wariancie otrzymuje „ma”. Warunki są osobnymi ograniczeniami:

- plan lub licencja;
- platforma albo IDE;
- model;
- region;
- wersja produktu;
- etap: eksperymentalna, preview, beta, GA;
- wymagane rozszerzenie lub integracja;
- inny warunek techniczny.

Każde ograniczenie ma własne źródło.

Funkcja otrzymuje „ma”, gdy jest natywna, realizowana przez integrację vendora lub rozwiązanie innej firmy oficjalnie dokumentowane i wspierane przez vendora. Otrzymuje wtedy ograniczenie integration_required.

Integracje społecznościowe i nieoficjalne obejścia nie wpływają na tabelę. Sama obecność w marketplace nie wystarcza do stwierdzenia oficjalnego wsparcia.

W UI komórka nadal pokazuje „MA”, ale ma wskaźnik ujawniający np. „tylko Enterprise”, „beta” lub „wymaga integracji”.

## 11. Źródła i polityki

Przy pierwszym badaniu system wyszukuje i zapisuje oficjalne źródła. Przy kolejnym czyta znane adresy i ponownie szuka nowych oficjalnych materiałów. Martwe linki, przekierowania i zmiany są raportowane.

Agent może dodać nowe, jednoznacznie oficjalne źródło w ramach przebiegu. Źródło wątpliwe jest pomijane i odnotowywane, jeżeli korpus pozostaje wystarczający.

System klasyfikuje rodzaj twierdzenia: bieżąca zdolność, wydanie lub wycofanie, etap dostępności, plan i cena, integracja, ograniczenie techniczne albo typ generic.

- bieżące działanie preferuje aktualną dokumentację;
- wydanie lub wycofanie preferuje changelog;
- plan preferuje cennik lub dokumentację licencji;
- integracja preferuje dokumentację integracji;
- nieznany typ używa polityki generic.

Semantyka znajduje się w skillu. Kolejność źródeł i fallback znajdują się w wersjonowanym YAML-u. YAML pozostaje prostą konfiguracją.

Konflikt rozstrzyga się przez: zgodność zakresu → stan bieżący kontra historia → aktualność → politykę typu → poszerzenie badania → „niepewne/sporne”.

System nie głosuje liczbą wystąpień, ponieważ wiele stron może kopiować tę samą informację.

## 12. Pełny protokół poszukiwania

Ukończenie protokołu jest warunkiem statusu „nie ma”.

### Etap 1 — logiczny korpus źródeł

Agent z użyciem narzędzi internetowych harnessu zbiera dokumentację, changelog, stronę produktową, cennik i licencjonowanie, katalog integracji, zapisane źródła specjalistyczne oraz nowe oficjalne materiały. Logiczny korpus jest rejestrem sprawdzonych źródeł, istotnych fragmentów, metadanych, zapytań, braków dostępu i powodów odrzucenia trafień. System nie wymaga lokalnego crawlera, pełnych kopii stron ani indeksu dokumentów.

### Etap 2 — cecha

Dla każdej cechy system:

1. szuka nazwy kanonicznej;
2. szuka aliasów i synonimów;
3. wyszukuje semantycznie w zarejestrowanych źródłach przy użyciu narzędzi harnessu;
4. przy braku trafień szuka celowanie w oficjalnych domenach;
5. zbiera wszystkie istotne fragmenty;
6. przekazuje je razem do klatki LLM;
7. zapisuje status, dowody, ograniczenia i ślad.

Brak dowodu po pełnym protokole daje „nie ma”. Brak możliwości wykonania istotnej części daje „niepewne/sporne”.

Wynik negatywny zapisuje potwierdzenie ukończenia protokołu, rodzaje źródeł, terminy i datę. Model nie decyduje sam, że szukał wystarczająco długo.

## 13. Klatka LLM

Wejście obejmuje jedną cechę z definicją, kryteria i wykluczenia, wszystkie fragmenty dotyczące cechy, metadane źródeł, politykę oraz kompletność protokołu.

Wyjście zgodne z JSON Schema zawiera feature_id, status, uzasadnienie, dowody, ograniczenia, politykę, ślad poszukiwania i dane konfliktu.

LLM nie używa wiedzy o produkcie spoza korpusu. Instrukcje znalezione na stronach są niezaufanymi danymi, nie poleceniami.

## 14. Profil semantyczny

Tabela nie ogranicza profilu. Profil może opisywać wewnętrzne mechanizmy, np. TaskList, architekturę użytkową, przepływy i informacje trudne do porównania.

Fakt spoza słownika jest zapisany jako additional_fact. Porównywalna zdolność może równolegle zostać kandydatem.

Zakres opisu jest edytowalny w pliku profile-sections.yaml, np. charakterystyka, dostęp, wewnętrzne narzędzia, przepływy, przypadki użycia, integracje, bezpieczeństwo i ograniczenia.

LLM tworzy opis z wyników cech, dowodów, korpusu, dodatkowych faktów i konfliktów. Może syntetyzować, ale nie dodawać faktów z pamięci.

Przypadki użycia mogą być:

- **udokumentowane** — wskazane przez vendora i poparte źródłem;
- **wnioskowane** — zaproponowane przez LLM na podstawie potwierdzonych zdolności.

Wniosek ma etykietę inferred, uzasadnienie, wspierające cechy i dowody. Nie wpływa na flagi.

## 15. Skill `/tool-eval-research`

Istnieje jedna operacja badawcza uruchamiana przez bezpośrednie wywołanie skilla `/tool-eval-research <tool>`. System nie korzysta z warstwy `.claude/commands/`.

Dla nowego narzędzia: odkrycie źródeł → logiczny korpus → badanie cech → fakty i kandydaci → kuracja lub poczekalnia → opis → walidacja → bezpieczna publikacja.

Dla istniejącego: sprawdzenie znanych i nowych źródeł → pełne badanie według aktualnego zakresu → walidacja → zastąpienie profilu. „Odśwież X” może być aliasem bez osobnej logiki.

Kandydaci są przedstawiani razem. Po akceptacji cechy system bada ją dla bieżącego narzędzia, a pozostałe profile oznacza `requires_research`. Kandydat odłożony przez operatora trafia do poczekalni.

## 16. Pełny przepływ działania mechanizmu

### 16.1 Przepływ end-to-end skilla `/tool-eval-research`

Z perspektywy użytkownika punktem wejścia jest bezpośrednie wywołanie skilla: **`/tool-eval-research X`**.

Operacja prowadzi operatora przez jeden punkt kuratorski, w którym rozpatrywani są wszyscy kandydaci wykryci w przebiegu.

    UŻYTKOWNIK: „/tool-eval-research X”
            │
            ▼
    [1. Inicjalizacja przebiegu]
            │
            ├─ identyfikacja narzędzia i zakresu badania
            ├─ identyfikator przebiegu
            ├─ wczytanie konfiguracji i schematów
            └─ sprawdzenie, czy profil istnieje
            │
            ▼
    [2. Przygotowanie źródeł]
            │
            ├─ nowe narzędzie: onboarding
            ├─ istniejące: kontrola zapisanych źródeł
            ├─ wyszukanie nowych źródeł
            └─ kontrola linków i przekierowań
            │
            ▼
    [3. Budowa logicznego korpusu]
            │
            ├─ przeglądanie źródeł przez agentów
            ├─ rejestr istotnych fragmentów i zapytań
            └─ klasyfikacja źródeł i braków dostępu
            │
            ▼
    [4. Badanie wszystkich cech]
            │
            ├─ nazwy, aliasy i wyszukiwanie semantyczne
            ├─ wyszukiwanie celowane przy braku trafień
            ├─ klatka LLM
            └─ status + dowody + ograniczenia + ślad
            │
            ▼
    [5. Poszerzenie profilu]
            │
            ├─ fakty dodatkowe
            ├─ wewnętrzne mechanizmy
            ├─ przypadki użycia
            └─ kandydaci na nowe cechy
            │
            ▼
    [6. Jeden punkt kuratorski]
            │
            ├─ akceptacja albo odrzucenie
            └─ odłożenie do poczekalni
            │
            ▼
    [7. Złożenie profilu]
            │
            ├─ dane strukturalne
            └─ opis semantyczny
            │
            ▼
    [8. Walidacja i naprawa]
            │
            ├─ JSON Schema
            ├─ reguły biznesowe
            └─ maksymalnie 3 próby naprawy
            │
            ▼
    [9. Bezpieczna publikacja profilu]
            │
            ├─ sukces: zastąpienie profilu
            └─ błąd: zachowanie poprzedniego
            │
            ▼
    [10. Raport dla użytkownika]

#### Krok 1 — inicjalizacja

Agent:

1. normalizuje nazwę narzędzia i rozpoznaje jego identyfikator;
2. ustala zakres badania;
3. nadaje identyfikator przebiegu;
4. wczytuje aktualny słownik cech, szablon profilu, polityki źródeł, progi świeżości i schematy;
5. sprawdza, czy istnieje aktywny profil i zapisane źródła narzędzia.

Jeżeli konfiguracja lub schema są niepoprawne, proces kończy się przed pobieraniem źródeł. Takiego błędu LLM nie próbuje naprawiać.

#### Krok 2 — przygotowanie źródeł

Dla nowego narzędzia system wykonuje onboarding: znajduje oficjalne domeny, dokumentację, changelog, stronę produktową, cennik i katalog integracji.

Dla istniejącego narzędzia zaczyna od zapisanych źródeł, ale dodatkowo szuka nowych oficjalnych materiałów. Ponowne badanie nie ogranicza się więc do historycznej listy URL-i.

Każde źródło otrzymuje typ, adres, datę sprawdzenia, status dostępności i informację o oficjalności. Martwe linki oraz przekierowania trafiają do raportu.

Jeżeli nie uda się zbudować minimalnego wiarygodnego korpusu, proces kończy się błędem i nie zmienia profilu.

#### Krok 3 — budowa logicznego korpusu

Agent i subagenci przeglądają strony przy użyciu narzędzi internetowych harnessu. Rejestrują sprawdzone URL-e, klasy źródeł, daty, zapytania, istotne fragmenty, braki dostępu oraz powody odrzucenia trafień.

Logiczny korpus jest wspólną podstawą badania cech i tworzenia szerszego profilu. Nie jest lokalnym archiwum stron ani indeksem wyszukiwawczym. Strony są traktowane jako niezaufane dane; zawarte w nich instrukcje nie mogą sterować agentem.

#### Krok 4 — badanie cech

Dla każdej aktualnej cechy wykonywany jest pełny protokół. Znalezione fragmenty są przekazywane razem do klatki LLM.

- Wynik „ma” albo „częściowo” zapisuje dowody i ograniczenia.
- Wynik „nie ma” zapisuje ukończony protokół poszukiwania.
- Wynik „niepewne/sporne” zapisuje przyczynę i istotne dowody.

Przetwarzanie cech może być zrównoleglone technicznie, ale każda cecha przechodzi identyczne reguły, a wyniki są składane w jeden profil.

#### Krok 5 — informacje szersze niż tabela

Po mapowaniu cech LLM analizuje korpus pod kątem informacji ważnych dla profilu, ale zbyt szczegółowych lub nieporównywalnych dla tabeli. Powstają fakty dodatkowe, opis mechanizmów, przepływy pracy oraz przypadki użycia.

Wyraźna zdolność spoza słownika jest równocześnie kandydatem. Informacja czysto kontekstowa może pozostać wyłącznie faktem profilowym.

#### Krok 6 — punkt kuratorski

System przedstawia wszystkich kandydatów razem. Operator może ich zaakceptować, odrzucić albo odłożyć.

Akceptacja nowej cechy powoduje:

1. dodanie jej do słownika;
2. zwiększenie rewizji słownika;
3. zbadanie jej dla bieżącego narzędzia w tym samym przebiegu;
4. oznaczenie innych profili jako wymagających ponownego badania.

#### Krok 7 — złożenie profilu

Agent składa wersję roboczą zawierającą:

- metadane narzędzia i przebiegu;
- datę badania oraz rewizje;
- źródła;
- wyniki wszystkich cech;
- ograniczenia;
- fakty dodatkowe;
- przypadki użycia;
- opis semantyczny;
- informacje niepewne i sporne.

#### Krok 8 — walidacja i naprawa

Najpierw uruchamiane jest JSON Schema, a potem walidator reguł biznesowych. Skrypt zwraca modelowi dokładną listę braków.

LLM naprawia wskazane rekordy, po czym cały profil jest walidowany ponownie. Dostępne są maksymalnie trzy próby naprawy po pierwszej generacji. Po ich wyczerpaniu przebieg kończy się błędem.

#### Krok 9 — bezpieczna publikacja profilu

Poprawny profil jest w całości przygotowywany i walidowany w katalogu przebiegu, a następnie zastępuje poprzedni katalog profilu. Na czas podmiany poprzedni katalog jest zachowywany jako kopia techniczna; błąd powoduje rollback. Data badania jest aktualizowana wyłącznie po sukcesie.

Przy błędzie wersja robocza nie staje się aktywnym profilem. Poprzedni wynik jest przywracany, a przyczyna trafia do raportu nieudanego przebiegu. Profil wewnętrzny może być chwilowo niedostępny podczas podmiany lub recovery, co nie wpływa na odbiorcę końcowego: widzi on dopiero osobno udostępniony, kompletny HTML wygenerowany po zakończeniu procesu.

#### Krok 10 — raport dla użytkownika

Po sukcesie użytkownik otrzymuje:

- potwierdzenie zapisu profilu;
- datę badania;
- liczbę sprawdzonych źródeł;
- liczbę cech w każdym statusie;
- liczbę ograniczeń;
- liczbę zaakceptowanych albo oczekujących kandydatów;
- informację, czy inne profile wymagają badania;
- ścieżkę do wyniku.

Po błędzie otrzymuje etap zatrzymania, przyczynę, liczbę wykorzystanych prób naprawy oraz potwierdzenie, że poprzedni profil nie został nadpisany.

### 16.2 Przepływ skilla `/tool-eval-compare`

Punktem wejścia jest bezpośrednie wywołanie skilla: **`/tool-eval-compare A B C`**.

    UŻYTKOWNIK: „/tool-eval-compare A B C”
            │
            ▼
    [1. Rozpoznanie narzędzi]
            │
            ▼
    [2. Wczytanie aktywnych profili]
            │
            ├─ brak profilu → błąd dla narzędzia
            └─ stara rewizja → ostrzeżenie
            │
            ▼
    [3. Kontrola dat i rewizji]
            │
            ├─ wiek danych
            └─ rozjazd dat
            │
            ▼
    [4. Zestawienie cech według kart]
            │
            ▼
    [5. Deterministyczne obliczenie flag]
            │
            ▼
    [6. Złożenie tabel i profili w HTML]
            │
            ▼
    [7. Walidacja i zapis artefaktu]
            │
            ▼
    [8. Raport dla użytkownika]

Skill nie uruchamia ponownego badania starych profili. Pokazuje ostrzeżenia i pozostawia decyzję operatorowi. Brakująca albo niezbadana cecha nie jest zamieniana na „nie ma” i nie uczestniczy w flagach.

Po sukcesie użytkownik otrzymuje datę porównania, listę użytych profili i ich dat, ostrzeżenia o świeżości oraz ścieżkę do HTML-a.

### 16.3 Główne ścieżki niepowodzenia

| Sytuacja | Zachowanie |
|---|---|
| Niepoprawna konfiguracja lub schema | Zakończenie przed badaniem |
| Brak wiarygodnych źródeł nowego narzędzia | Brak utworzenia profilu |
| Częściowa niedostępność źródeł | „Niepewne/sporne”, jeśli nadal można zbudować poprawny profil |
| Zbyt duża utrata źródeł | Odrzucenie przebiegu i zachowanie starego profilu |
| Naprawialny błąd walidacji | Maksymalnie trzy próby naprawy |
| Błąd po trzech próbach | Odrzucenie przebiegu |
| Brak profilu przy porównaniu | Komunikat wskazujący narzędzie wymagające badania |
| Profil ze starą rewizją | Porównanie z ostrzeżeniem, bez flag dla niekompletnych cech |
## 17. Walidacja i zapis

### Dwie warstwy

JSON Schema kontroluje strukturę i typy. Walidator biznesowy kontroluje:

- jeden wynik każdej cechy;
- dowody dla „ma” i „częściowo”;
- protokół dla „nie ma”;
- przyczynę dla „niepewne/sporne”;
- źródła ograniczeń;
- poprawność identyfikatorów;
- datę, rewizje i wymagane sekcje;
- rozpatrzenie albo odłożenie kandydatów.

### Pętla naprawcza

Walidator zwraca kod błędu, ścieżkę, feature_id i opis. LLM dostaje wadliwy fragment, źródła oraz błędy. Po poprawce cały profil jest walidowany ponownie.

Dopuszcza się maksymalnie trzy próby naprawy po pierwszej generacji. Błąd nienaprawialny przez LLM kończy proces od razu.

### Publikacja

Nowy profil zastępuje aktywny dopiero po pełnym sukcesie walidacji stagingu. Podmiana korzysta z kopii technicznej, rollbacku i recovery. Przy porażce poprzedni profil oraz jego data są przywracane, niepełny wynik nie jest publikowany, a próba jest raportowana. Raport HTML jest odrębnym, zamrożonym artefaktem udostępnianym odbiorcy dopiero po zakończeniu generowania.

## 18. Porównanie i flagi

Skill `/tool-eval-compare A B C` pobiera profile, sprawdza rewizje i daty, zestawia dane, liczy flagi skryptem i generuje HTML.

Porównanie może powstać mimo profili requires_research, lecz pokazuje ostrzeżenie. Niezbadane komórki nie są „nie ma” i nie uczestniczą w flagach.

- „ma” z ograniczeniem liczy się jako „ma”;
- „częściowo” nie liczy się jako „ma” ani „nie ma”;
- „niepewne/sporne” i niezbadana komórka wyłączają cechę z flag;
- wystąpienie „częściowo” daje „zróżnicowana realizacja”.

Flagi rozkładu wymagają minimum czterech narzędzi i kompletu jednoznacznych wyników:

- **Tylko jeden ma** — jedno „ma”, reszta „nie ma”.
- **Tylko jeden nie ma** — jedno „nie ma”, reszta „ma”.
- **Rzadkie** — dwa „ma”, reszta „nie ma”.
- **Powszechne w tym zestawieniu** — wszyscy mają lub jeden nie ma.
- **Podzielone** — różnica liczby „ma” i „nie ma” wynosi maksymalnie jeden.
- **Zróżnicowana realizacja** — występuje „częściowo”.

Flagi mogą współistnieć. Zawsze odnoszą się do badanego zestawu, nie całego rynku.

## 19. Świeżość

Każdy profil ma datę badania, a porównanie datę wygenerowania.

- 0–30 dni — aktualne;
- 31–60 dni — starzejące się;
- ponad 60 dni — nieaktualne;
- rozjazd ponad 14 dni między profilami — ostrzeżenie.

Progi są konfigurowalne w YAML-u. System ostrzega, ale nie wymusza badania.

## 20. Sekcja B — Etap 2

Sekcja B zawiera twarde benchmarki, bez sentymentu i opinii.

Główna zakładka reprezentuje podmiot wykonujący lub dostarczający ocenę. Wewnątrz są osobne tabele benchmarków i porównywalnych konfiguracji. Różnych konfiguracji nie scala się w jeden ranking.

Każdy wynik rozróżnia:

- benchmark_owner — twórcę benchmarku;
- evaluator — wykonawcę pomiaru;
- publisher — publikującego.

Jeżeli vendor cytuje leaderboard, dostawcą wyniku pozostaje operator leaderboardu.

Źródło jest oznaczone jako: oficjalny leaderboard, niezależny pomiar, vendor oceniający siebie, vendor porównujący konkurencję albo strona trzecia. Wyniki vendorów pozostają widoczne z jawnym konfliktem interesów.

Pomiar zawiera benchmark i wersję, harness, metrykę i tryb, model, wersję narzędzia, konfigurację, wynik, datę, wykonawcę, publikującego, źródło i informację o weryfikacji.

Bezpośrednie porównanie wymaga zgodności kluczowych warunków. Inne pomiary są pokazywane osobno. Brak wyniku oznacza brak opublikowanego pomiaru, nie zero.

Hierarchia: oficjalny leaderboard → niezależna publikacja lub paper → raport vendora → źródło trzecie. Inne wyniki nie są usuwane; zakładki pokazują rozbieżności.

## 21. Role techniczne

**Agent** prowadzi research, pilnuje faz, kuracji, walidacji i bezpiecznej publikacji.

**Skille wejściowe** `/tool-eval-research`, `/tool-eval-compare` i `/tool-eval-resume` są bezpośrednimi punktami wejścia użytkownika. **Skille domenowe** opisują onboarding, typy twierdzeń, badanie cech, konflikty, kandydatów, profil i Sekcję B.

**Skrypty** utrzymują stan przebiegu, przygotowują manifesty, walidują dane i kompletność śladu, scalają wyniki, zarządzają rewizjami, liczą flagi, sprawdzają świeżość, generują HTML oraz publikują i przywracają profile.

Treść stron jest niezaufana. Prompt injection nie może sterować agentem.

## 22. Konfiguracja

Logiczny podział:

- config/source-policies.yaml;
- config/freshness.yaml;
- config/profile-sections.yaml;
- config/feature-taxonomy.yaml;
- config/tools/;
- schemas/;
- data/profiles/;
- data/feature-candidates/;
- .work/failed-runs/;
- outputs/comparisons/.

Nazwy są propozycją. Wymagane jest oddzielenie konfiguracji od instrukcji skilla, profili od porównań, kandydatów od słownika i błędnych przebiegów od aktywnych danych.

## 23. Wymagania niefunkcjonalne

- **Transparentność:** dowody, ślad wyników negatywnych, źródła ograniczeń, przyczyny konfliktów i daty.
- **Rozszerzalność:** nowe narzędzie przez `/tool-eval-research X`, nowe cechy przez poczekalnię, edytowalne sekcje i polityki.
- **Spójność:** niepełny profil nie zastępuje poprawnego; awaria nie zmienia cicho „ma” w „nie ma”.
- **Bezpieczeństwo:** sanitacja HTML-u, bezpieczne linki, brak wykonywania kodu ze źródeł i brak sekretów.
- **Samowystarczalność:** HTML działa lokalnie bez backendu.
- **Koszt:** konfigurowalne limity czasu, źródeł i wywołań LLM; przekroczenie limitu nie zapisuje niepełnego profilu.

## 24. Kryteria akceptacji Etapu 1

1. `/tool-eval-research X` tworzy profil nowego narzędzia.
2. Ponowne badanie używa znanych i szuka nowych oficjalnych źródeł.
3. Każda aktualna cecha ma jeden poprawny wynik.
4. Wyniki mają wymagane dowody albo ślad protokołu.
5. Ograniczenia są strukturalne, źródłowe i widoczne w UI.
6. Oficjalna integracja może dać „ma”; społecznościowa nie wpływa na status.
7. Kandydaci są kuratorowani razem albo trafiają do poczekalni.
8. Zmiana słownika lub szablonu oznacza starsze profile.
9. Walidator zwraca konkretne błędy i uruchamia najwyżej trzy naprawy.
10. Nieudane badanie nie zmienia profilu ani daty.
11. `/tool-eval-compare` tworzy samowystarczalny HTML z kartami i profilami.
12. Flagi są deterministyczne, a niekompletne cechy wyłączone.
13. HTML pokazuje daty, wiek i rozjazd.
14. Profil zawiera opis LLM, fakty dodatkowe i oba typy przypadków użycia.
15. Treść stron nie może sterować agentem ani wykonywać kodu w HTML-u.

## 25. Plan implementacji

1. **Fundament:** słownik 20–30 cech, stabilne ID, schemat, konfiguracje i walidator.
2. **Pojedyncze narzędzie:** onboarding, logiczny korpus, klatka LLM, ograniczenia, profil i publikacja.
3. **Porównanie:** tabele, flagi, świeżość, nawigacja i HTML.
4. **Obsługa operacyjna:** poczekalnia, raporty, recovery i limity.
5. **Sekcja B:** schemat pomiarów, dostawcy, porównywalność i zakładki.

## 26. Otwarte szczegóły implementacyjne

Plan implementacji rozstrzyga architekturę i konwencje, które w poprzedniej wersji dokumentu pozostawały otwarte. Przyjęte zostały w szczególności:

- model profilu, podział odpowiedzialności między JSON Schema i walidator biznesowy oraz konwencje schematów — D-016;
- rodziny kodów błędów, zawartość rekordu błędu, retry, failed runs i resume — D-011;
- postać logicznego rejestru źródeł, zakres przechowywanych dowodów i protokół wyników negatywnych — D-006 i D-009;
- format profilu, artefaktów przebiegu i nieudanych prób — D-007, D-011 i sekcja 3 planu;
- minimalny stos zależności, sposób budowy samowystarczalnego HTML-a i wspierane przeglądarki — D-013 i D-014;
- Claude Code jako harness MVP oraz bezpośrednio wywoływane skille użytkownika — D-015 i D-018.

Otwarte pozostają wyłącznie szczegóły realizacyjne, które nie blokują rozpoczęcia implementacji:

- ostateczna treść poszczególnych JSON Schema w ramach przyjętego modelu;
- dokładne instrukcje skilli dla klatki LLM i pierwsze przykłady walidacyjne;
- początkowe grupy i 20–30 cech przygotowywanych pod nadzorem kuratora;
- specjalistyczne klasy oficjalnych źródeł wymagane dla konkretnych narzędzi;
- konkretne limity czasu, pracy i wyszukiwań, kalibrowane podczas pilotażu;
- dokładne wersje zależności w przyjętych zakresach, wybierane po sprawdzeniu instalacji i głównych przepływów;
- lista benchmarków i szczegółowe kontrakty Etapu 2.

Zmiana którejkolwiek z przyjętych decyzji wymaga aktualizacji planu implementacji, a jeżeli wpływa na zachowanie produktu lub kryteria akceptacji — również niniejszego dokumentu wymagań.

## 27. Przyjęte kompromisy

System świadomie:

- uznaje brak potwierdzenia po pełnym protokole za „nie ma”;
- uznaje ograniczoną lub oficjalnie integrowaną funkcję za „ma”, eksponując warunki;
- pozwala LLM tworzyć szerszy opis i wnioskować przypadki użycia z jawną etykietą;
- nie przechowuje historii profili;
- dopuszcza porównanie starszych profili, ale wyłącza niezbadane cechy z flag;
- używa jednego przepływu `/tool-eval-research X`, uruchamianego przez bezpośrednie wywołanie skilla na żądanie operatora;
- rozdziela zdolności od skuteczności;
- wdraża Sekcję B po ustabilizowaniu Etapu 1;
- pozostawia operatorowi kurację, a skryptom walidację i arytmetykę.

Najważniejszym miernikiem jakości jest możliwość zrozumienia, skąd pochodzi wniosek, na jaki dzień jest aktualny i jakie ograniczenia wpływają na jego znaczenie.
