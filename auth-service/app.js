const express = require("express");
const jwt = require("jsonwebtoken");

const app = express();
app.use(express.json());

// ---- Config (set via docker-compose env in real use) ----
const PORT = process.env.PORT || 5001;
const JWT_SECRET = process.env.JWT_SECRET || "dev_secret_change_me";
const TOKEN_TTL_SECONDS = parseInt(process.env.TOKEN_TTL_SECONDS || "3600", 10);

// Hardcoded users (simple, per your requirement)
const USERS = {
  admin: "admin123",
  user: "user123",
};

// Health check
app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok" });
});

// POST /login { username, password } -> { token, expires_in }
app.post("/login", (req, res) => {
  const { username, password } = req.body || {};

  if (!username || !password) {
    return res.status(400).json({ error: "username and password required" });
  }

  const expected = USERS[username];
  if (!expected || expected !== password) {
    return res.status(401).json({ error: "invalid credentials" });
  }

  const token = jwt.sign(
    { sub: username }, // subject = username
    JWT_SECRET,
    { expiresIn: TOKEN_TTL_SECONDS }
  );

  return res.status(200).json({ token, expires_in: TOKEN_TTL_SECONDS });
});

// GET /verify with Authorization: Bearer <token> -> { valid: true, username }
app.get("/verify", (req, res) => {
  const authHeader = req.headers.authorization || "";
  const [scheme, token] = authHeader.split(" ");

  if (scheme !== "Bearer" || !token) {
    return res.status(401).json({ valid: false, error: "missing bearer token" });
  }

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    return res.status(200).json({ valid: true, username: payload.sub });
  } catch (err) {
    return res.status(401).json({ valid: false, error: "invalid or expired token" });
  }
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`auth-service listening on 0.0.0.0:${PORT}`);
});
