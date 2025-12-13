// This is a basic authentication system for content access
// In a real implementation, this would connect to a proper authentication service

// Middleware for checking if user is authenticated
function requireAuth(req, res, next) {
  // Check if user is authenticated (simplified example)
  const isAuthenticated = req.session && req.session.user;
  
  if (isAuthenticated) {
    next(); // User is authenticated, continue to the requested page
  } else {
    // Redirect to login page if not authenticated
    res.redirect('/login');
  }
}

// Login endpoint
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  
  // In a real implementation, verify credentials against a database
  // This is a simplified example with hardcoded credentials
  if (username === 'student' && password === 'robotics123') {
    // Create a session for the user
    req.session.user = { username: username };
    res.json({ success: true, message: 'Login successful' });
  } else {
    res.status(401).json({ success: false, message: 'Invalid credentials' });
  }
});

// Logout endpoint
app.post('/api/logout', (req, res) => {
  // Destroy the user session
  req.session.destroy((err) => {
    if (err) {
      res.status(500).json({ success: false, message: 'Could not log out' });
    } else {
      res.json({ success: true, message: 'Logout successful' });
    }
  });
});

// Registration endpoint
app.post('/api/register', (req, res) => {
  const { username, email, password } = req.body;
  
  // In a real implementation, validate inputs and store user in database
  // This is a simplified example
  if (username && email && password) {
    // Store user in database (not implemented in this example)
    res.json({ success: true, message: 'Registration successful' });
  } else {
    res.status(400).json({ success: false, message: 'Invalid registration data' });
  }
});

// Profile endpoint - protected route
app.get('/api/profile', requireAuth, (req, res) => {
  res.json({ 
    success: true, 
    user: req.session.user,
    message: 'Profile data retrieved successfully' 
  });
});

// Example of protecting a specific route
app.get('/docs/restricted-content', requireAuth, (req, res) => {
  // Serve restricted content to authenticated users
  res.sendFile(path.join(__dirname, '../docs/restricted-content.md'));
});