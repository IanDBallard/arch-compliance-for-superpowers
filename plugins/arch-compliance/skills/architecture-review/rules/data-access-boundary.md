# Rule: data-access-boundary

**Principle.** Access control is enforced at the data layer, not trusted to the client.
A table the client can reach has row-level security enabled; a privileged credential
never reaches client code; replication to clients filters by the authenticated user.

This rule says *where* enforcement must live. It does not judge whether a policy's
logic is correct, and it is not a general security review.

## Settings

- `surface`, `surface_exclude`: already applied by the controller. The surface bounds
  where a finding may be cited: every finding's line is in it.
- `docs`: documents to read in full before auditing (for example the data access
  design note).
- `client_paths`: path patterns of client code (code that runs in a browser, a mobile
  app or any other place the end user controls). When empty, no table is reachable
  through client code and check 2 is off.
- `policy_files`: path patterns of the files that define the database's access
  policies (migrations, schema files, policy declarations). Read every matching file.
  When empty, no table has row-level security enabled as far as this rule can see.
- `privileged_credentials`: the names of credentials that bypass access policies
  (service-role keys, admin tokens, the environment variable names that hold them).
  When empty, check 2 is off.
- `replication_rules`: path patterns of the files whose queries select rows sent to
  clients (sync rules, replication publications, subscription definitions). When
  empty, no table is reachable through replication and check 3 is off.

Files matching `{client_paths}`, `{policy_files}` and `{replication_rules}` are
evidence: read them wherever they are in the repository, inside the surface or not.
Only the line a finding cites must be in the surface.

An absent scalar turns its check off; an absent list is empty. When `client_paths`
and `replication_rules` are both empty, every check is off: report no findings and
add one `errors` string, `"check off: client_paths and replication_rules absent"`.

## Client-reachable tables

A table is **client-reachable** when code under `{client_paths}` names it (a query
builder call, a table name in a request, a generated type used to query it) or a query
in a file under `{replication_rules}` selects it. Build this set first.

## Flag

1. **No row-level security.** A client-reachable table on which no file under
   `{policy_files}` enables row-level security. Cite the table's create statement if it
   is in the surface; otherwise the first line in the surface, under `{client_paths}`
   or `{replication_rules}`, that names the table. When no such line is in the
   surface, name the table in `errors` instead.
2. **Privileged credential in client code.** A name from `{privileged_credentials}`
   appearing in a file under `{client_paths}`: read, imported, passed to a client
   constructor, or embedded.
3. **Unfiltered replication.** A query in `{replication_rules}` that selects a
   client-reachable table's rows without filtering by the authenticated user (or by a
   membership the authenticated user is checked against).

## Do not flag

- Tables only server code names, absent from `{replication_rules}`.
- A privileged credential named in server code, build configuration that does not ship
  to the client, or documentation.
- A replication query over data the doctrine section or `docs` declare public to every
  user (cite the declaration in `why` if you are unsure, as a `suggestion`).
- Whether a policy's condition is right: only that enforcement exists at the data layer.

## Severity

- `blocking`: check 1 (client-reachable table without row-level security); check 2
  (privileged credential in client code).
- `important`: check 3 (replication without a user filter).
- `nit`: a privileged credential's name in a client-side comment or dead code.
- `suggestion`: a table whose reachability or policy coverage you cannot determine;
  name the doubt in `why`.
