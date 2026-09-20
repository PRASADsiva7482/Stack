# 26. Testing, Maven, Git, and CI/CD

**Status:** Learning target.  
**Resume boundary:** The original resume supports JUnit, Git, GitLab, Maven, CI/CD support, and collaboration. It does not prove ownership of the entire delivery platform.

## 1. The professional model

Testing gives confidence in behavior. Maven makes the build reproducible. Git records change history. CI/CD automates verification and delivery. They are related but not interchangeable:

```text
change -> compile -> unit tests -> integration tests -> package -> scan -> publish -> deploy -> verify -> rollback if needed
```

The goal is fast feedback for cheap failures and realistic verification for expensive failures.

## 2. Test pyramid and boundaries

| Test | Best target | Speed | Typical dependency |
|---|---|---:|---|
| Unit | One class and its decisions | Fast | Fakes/mocks only at true boundaries |
| Slice | MVC, JSON, JPA mapping | Fast-medium | Selected Spring infrastructure |
| Integration | Several real components together | Medium | Test database, broker, or container |
| Contract | Provider/consumer API agreement | Medium | Pact/Spring Cloud Contract style tooling |
| End-to-end | Business journey across deployed services | Slow | Real environment |
| Load/performance | Capacity and latency behavior | Slow | Controlled environment and metrics |

Mock behavior you do not own: a payment gateway, clock, message publisher, or remote client. Do not mock the class under test, value objects, simple DTOs, or the database for every repository test. A mock can prove that a call happened; it cannot prove that a real SQL query, transaction, serialization format, or schema works.

## 3. JUnit 5 and Mockito essentials

```java
class BalanceServiceTest {
    private final Ledger ledger = mock(Ledger.class);
    private final BalanceService service = new BalanceService(ledger);

    @Test
    void rejectsNegativeAdjustment() {
        assertThatThrownBy(() -> service.adjust("sub-1", -1))
            .isInstanceOf(IllegalArgumentException.class);
        verifyNoInteractions(ledger);
    }

    @Test
    void recordsPositiveAdjustment() {
        service.adjust("sub-1", 10);
        verify(ledger).append("sub-1", 10);
    }
}
```

Good tests make the behavior obvious, isolate one reason to fail, use meaningful names, and assert observable outcomes. Avoid `verify` for every internal call; that locks the design and makes refactoring painful. Test exceptions, boundaries, duplicate requests, invalid input, time, and partial failures.

## 4. Spring Boot tests

- `@WebMvcTest`: controller, validation, serialization, exception mapping; mock the service boundary.
- `@DataJpaTest`: repository queries and mappings against a test database; verify generated SQL behavior.
- `@SpringBootTest`: full context; use sparingly because it is slower and can hide the failing layer.
- `MockMvc` tests HTTP status, headers, JSON, validation, and security filters without a real port.
- Testcontainers runs realistic PostgreSQL/MySQL/Kafka/Redis dependencies. Pin versions and clean data between tests.
- WireMock or an equivalent stub simulates downstream status codes, latency, malformed payloads, and timeouts.

An integration test should answer “does this boundary work?” A unit test should answer “does this decision work?”

## 5. Maven notes

The lifecycle commonly used in interviews is:

```text
validate -> compile -> test -> package -> verify -> install -> deploy
```

Know `pom.xml`, dependency scopes, transitive dependencies, plugins, profiles, properties, BOM/dependency management, and reproducible version pinning.

Useful diagnostics:

```powershell
mvn test
mvn -DskipTests package
mvn dependency:tree
mvn help:effective-pom
mvn -U clean verify
```

`-DskipTests` compiles tests but does not run them; `-Dmaven.test.skip=true` skips compiling and running tests. Neither is an acceptable permanent CI workaround. When a dependency conflict occurs, inspect the tree, identify the version selected by Maven, use dependency management or exclusions deliberately, and run the relevant tests.

## 6. Git interview essentials

```text
git status
git log --oneline --decorate --graph -20
git diff
git add -p
git commit
git fetch origin
git rebase origin/main
git cherry-pick <commit>
git revert <commit>
git tag -a v1.2.0 -m "release"
```

- `revert` creates a new inverse commit and is normally safe on shared history.
- `reset` moves a branch reference and can discard local work; explain `--soft`, `--mixed`, and `--hard` before using it.
- `rebase` rewrites local commit ancestry; do not rewrite commits others have based work on without agreement.
- A merge conflict is resolved by understanding both changes, editing, testing, staging, and continuing—not by choosing “ours” blindly.
- A good commit is small, buildable, and explains intent. A pull request should include risk, tests, migration/rollback impact, and observability.

## 7. CI/CD pipeline design

```text
PR: compile + unit + static analysis + secret/dependency scan
    -> integration/contract tests
merge: package immutable artifact -> publish checksum/tag
deploy: dev -> staging -> smoke/e2e -> canary or rolling production
post-deploy: health, error rate, latency, business metric -> promote/rollback
```

Blue-green keeps two environments and shifts traffic. Canary sends a small percentage to the new version. Rolling replaces instances gradually. All need backward-compatible database migrations, immutable artifacts, health checks, and a rollback plan. Rollback application code does not automatically roll back a destructive database migration.

### Honest resume answer

> “I supported GitLab CI/CD by contributing code, tests, build fixes, and deployment troubleshooting within the team pipeline. I can explain the stages and failure modes, but I would not claim that I owned the organization-wide CI/CD platform unless I had designed and operated it.”

## 8. Common failures and investigation

| Symptom | First checks | Likely causes |
|---|---|---|
| Build works locally, CI fails | JDK/Maven versions, clean checkout, environment | Undeclared dependency, profile drift, line endings |
| Test flaky | Repeat test, logs, shared state, clock | Race, clock, random data, leaked container |
| Dependency CVE | Dependency tree and scanner path | Transitive dependency, unpinned plugin |
| Deployment healthy but feature fails | API contract, config, migration, logs | Incompatible release order |
| Rollback does not fix issue | Version, data/schema, cache, flags | State changed outside app binary |

## 9. Practice

1. Build a Spring Boot CRUD service with unit, MVC, repository, WireMock, and Testcontainers tests.
2. Add a GitLab-like pipeline locally with compile, test, package, scan placeholder, and artifact checksum.
3. Create a deliberately conflicting branch, resolve it, rebase it, and explain why revert is safer than reset on a shared branch.
4. Add a backward-compatible database migration, deploy old and new application versions, and test both.

## 10. Interview questions

1. What is the test pyramid and why not write only end-to-end tests?
2. What should be mocked in a service unit test?
3. How do you test a controller without loading the entire application?
4. When would you use Testcontainers?
5. How do you test retries and timeouts deterministically?
6. Why is a flaky test a production problem?
7. Explain Maven dependency mediation and BOMs.
8. What is the difference between `mvn test`, `verify`, and `package`?
9. Rebase versus merge?
10. Revert versus reset?
11. How do you safely release a schema change?
12. What evidence do you need before declaring a deployment successful?

## 11. Production scenario

**A deployment passes CI but causes 500 errors.** Freeze promotion, compare error and trace rates against the previous version, inspect changed endpoints and configuration, check migration compatibility, reproduce with the same payload, and determine whether rollback is safe. If the schema changed, use the compatible code path or a forward fix. Add a regression test and an alert/dashboard for the failure mode.

## 12. Senior answer

> “I use fast tests for business decisions, realistic integration tests for framework and data boundaries, and a small number of end-to-end tests for critical journeys. The pipeline should produce an immutable artifact, deploy only after compatibility checks, verify health and business signals, and make rollback explicit. Since my resume says CI/CD support, I describe my contributions precisely and separate them from platform ownership.”

