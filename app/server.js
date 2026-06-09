const express = require("express");
const jwt = require("jsonwebtoken");
const serialize = require("node-serialize");
const { exec } = require("child_process");

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// BUG: Hardcoded JWT secret embedded in source code.
const JWT_SECRET = "secret123";

// BUG: Hardcoded database credentials.
const DB_CONFIG = {
  host: "prod-db.internal",
  user: "root",
  password: "root1234",
  database: "appdb",
};


// BUG: Reflected XSS - user input rendered into HTML without escaping.
app.get("/search", (req, res) => {
  const query = req.query.q;
  res.send(`<h1>Search results for: ${query}</h1>`);
});


// BUG: Command injection - user-supplied filename passed directly to exec().
app.get("/file-info", (req, res) => {
  const filename = req.query.name;
  exec("ls -la " + filename, (err, stdout) => {
    res.send(stdout);
  });
});


// BUG: Insecure deserialization via node-serialize - allows remote code execution
// when attacker sends a crafted serialized object with IIFE payload.
app.post("/restore-session", (req, res) => {
  const sessionData = req.body.session;
  const obj = serialize.unserialize(sessionData);
  res.json({ user: obj.user });
});


// BUG: JWT verification disabled - algorithm set to "none" accepts unsigned tokens.
app.get("/profile", (req, res) => {
  const token = req.headers.authorization;
  const decoded = jwt.verify(token, JWT_SECRET, { algorithms: ["none", "HS256"] });
  res.json(decoded);
});


// BUG: JWT secret is weak and hardcoded; token forgery is trivial.
app.post("/login", (req, res) => {
  const { username } = req.body;
  const token = jwt.sign({ username, role: "user" }, JWT_SECRET);
  res.json({ token });
});


// BUG: Prototype pollution - merging user input into an object without key sanitisation
// lets an attacker inject __proto__ and pollute the Object prototype.
app.post("/settings", (req, res) => {
  const userSettings = req.body;
  const defaults = { theme: "light", lang: "en" };

  function merge(target, source) {
    for (const key in source) {
      target[key] = source[key];
    }
    return target;
  }

  const config = merge(defaults, userSettings);
  res.json(config);
});


// BUG: Open redirect - next parameter is not validated before redirecting.
app.get("/logout", (req, res) => {
  const next = req.query.next || "/";
  res.redirect(next);
});


// BUG: SQL injection via string concatenation (using hypothetical db.query).
app.get("/user", (req, res) => {
  const userId = req.query.id;
  const query = "SELECT * FROM users WHERE id = " + userId;
  // db.query(query) would execute an injectable query here
  res.json({ query });
});


app.listen(3000);
