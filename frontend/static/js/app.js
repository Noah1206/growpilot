// API Configuration
// Use same origin for API (backend serves frontend)
const API_BASE_URL = window.location.hostname === 'localhost'
    ? "http://localhost:8001"
    : window.location.origin;

// Auth state management
let isLoggedIn = false;

// Modal functions
function showLoginModal() {
  document.getElementById('loginModal').style.display = 'block';
  document.getElementById('loginError').style.display = 'none';
}

function closeLoginModal() {
  document.getElementById('loginModal').style.display = 'none';
}

function showSignupModal() {
  document.getElementById('signupModal').style.display = 'block';
  document.getElementById('signupError').style.display = 'none';
  document.getElementById('signupSuccess').style.display = 'none';
}

function closeSignupModal() {
  document.getElementById('signupModal').style.display = 'none';
}

function switchToSignup(event) {
  event.preventDefault();
  closeLoginModal();
  showSignupModal();
}

function switchToLogin(event) {
  event.preventDefault();
  closeSignupModal();
  showLoginModal();
}

// Close modal when clicking outside
window.onclick = function(event) {
  const loginModal = document.getElementById('loginModal');
  const signupModal = document.getElementById('signupModal');
  if (event.target == loginModal) {
    closeLoginModal();
  }
  if (event.target == signupModal) {
    closeSignupModal();
  }
}

// Auth functions
function checkAuth() {
  const token = localStorage.getItem('token');
  isLoggedIn = !!token;

  const loggedInMenu = document.getElementById('loggedInMenu');
  const loggedOutMenu = document.getElementById('loggedOutMenu');

  if (isLoggedIn) {
    loggedInMenu.style.display = 'flex';
    loggedOutMenu.style.display = 'none';

    // Display user email
    const userEmail = localStorage.getItem('user_email');
    if (userEmail) {
      document.getElementById('userEmail').textContent = userEmail;
    }
  } else {
    loggedInMenu.style.display = 'none';
    loggedOutMenu.style.display = 'flex';
  }

  return isLoggedIn;
}

async function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Login failed');
    }

    // Store token and email
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user_email', email);

    console.log('✅ Token saved to localStorage');

    // Close modal and update UI
    closeLoginModal();
    checkAuth();

    // Clear form
    document.getElementById('loginEmail').value = '';
    document.getElementById('loginPassword').value = '';

  } catch (error) {
    const errorDiv = document.getElementById('loginError');
    errorDiv.textContent = error.message;
    errorDiv.style.display = 'block';
  }
}

async function handleSignup(event) {
  event.preventDefault();

  const name = document.getElementById('signupName').value;
  const email = document.getElementById('signupEmail').value;
  const password = document.getElementById('signupPassword').value;

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
        full_name: name || undefined
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Signup failed');
    }

    // Show success message
    const successDiv = document.getElementById('signupSuccess');
    successDiv.textContent = 'Account created successfully! You can now login.';
    successDiv.style.display = 'block';

    // Clear form
    document.getElementById('signupName').value = '';
    document.getElementById('signupEmail').value = '';
    document.getElementById('signupPassword').value = '';

    // Switch to login after 2 seconds
    setTimeout(() => {
      closeSignupModal();
      showLoginModal();
      document.getElementById('loginEmail').value = email;
    }, 2000);

  } catch (error) {
    const errorDiv = document.getElementById('signupError');
    errorDiv.textContent = error.message;
    errorDiv.style.display = 'block';
  }
}

function handleLogout() {
  // Remove token
  localStorage.removeItem('token');
  localStorage.removeItem('user_email');
  checkAuth();
}

function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  };
}

// Check auth on page load
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
});

// Form submission handler (only for index.html)
const campaignForm = document.getElementById("campaignForm");
if (campaignForm) {
  campaignForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Check if logged in
    if (!isLoggedIn) {
      alert('Please login first to generate campaigns');
      showLoginModal();
      return;
    }

    // Show loading
    document.getElementById("loading").style.display = "block";
    document.getElementById("results").style.display = "none";
    document.getElementById("error").style.display = "none";

    // Collect form data
    const localesValue = document.getElementById("locales").value.trim();
    const locales = localesValue
      ? localesValue
          .split(",")
          .map((s) => s.trim())
          .filter((s) => s.length > 0)
      : ["US"]; // Default to US if empty

    const channels = Array.from(
      document.querySelectorAll('input[name="channels"]:checked')
    ).map((cb) => cb.value);

    // Validate at least one channel is selected
    if (channels.length === 0) {
      alert(
        "Please select at least one channel (LinkedIn, Reddit, or Facebook)"
      );
      document.getElementById("loading").style.display = "none";
      return;
    }

    const formData = {
      product_name: document.getElementById("productName").value,
      description: document.getElementById("description").value,
      tracking_url: document.getElementById("trackingUrl").value,
      target_audience_hint: document.getElementById("targetAudience").value || null,
      locales: locales,
      language_pref: document.getElementById("language").value,
      channels: channels,
      tone: document.getElementById("tone").value,
      cta: document.getElementById("cta").value || null,
    };

    try {
      // Call API
      const response = await fetch(`${API_BASE_URL}/api/campaigns/generate`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        if (response.status === 401) {
          alert('Your session has expired. Please login again.');
          handleLogout();
          showLoginModal();
          return;
        }
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Display results
      displayResults(data);
    } catch (error) {
      console.error("Error:", error);
      document.getElementById("loading").style.display = "none";
      document.getElementById("error").style.display = "block";
      document.getElementById(
        "errorMessage"
      ).textContent = `Failed to generate campaign: ${error.message}. Please check that the backend server is running on ${API_BASE_URL}`;
    }
  });
}

// Display results
function displayResults(data) {
  document.getElementById("loading").style.display = "none";
  document.getElementById("results").style.display = "block";

  // Display ICP
  if (data.icp) {
    displayICP(data.icp);
  }

  // Display Queries
  if (data.queries) {
    displayQueries(data.queries);
  }

  // Display LinkedIn Copy (if element exists)
  const linkedinSection = document.getElementById("linkedinSection");
  if (linkedinSection) {
    if (data.linkedin_copy) {
      linkedinSection.style.display = "block";
      displayCopy("linkedinResults", data.linkedin_copy);
    } else {
      linkedinSection.style.display = "none";
    }
  }

  // Display Reddit Copy
  if (data.reddit_copy) {
    document.getElementById("redditSection").style.display = "block";
    displayCopy("redditResults", data.reddit_copy);
  } else {
    document.getElementById("redditSection").style.display = "none";
  }

  // Display Facebook Copy
  if (data.facebook_copy) {
    document.getElementById("facebookSection").style.display = "block";
    displayCopy("facebookResults", data.facebook_copy);
  } else {
    document.getElementById("facebookSection").style.display = "none";
  }

  // Display Policy Review
  if (data.policy_review) {
    displayPolicyReview(data.policy_review);
  }
}

// Display ICP
function displayICP(icpData) {
  const container = document.getElementById("icpResults");
  const icp = icpData.icp || {};
  const keywords = icpData.keywords || {};

  let html = '<div class="icp-grid">';

  // Roles
  if (icp.roles && icp.roles.length > 0) {
    html += `
            <div class="icp-item">
                <h4>Target Roles</h4>
                <ul>
                    ${icp.roles.map((role) => `<li>${role}</li>`).join("")}
                </ul>
            </div>
        `;
  }

  // Industries
  if (icp.industries && icp.industries.length > 0) {
    html += `
            <div class="icp-item">
                <h4>Industries</h4>
                <ul>
                    ${icp.industries.map((ind) => `<li>${ind}</li>`).join("")}
                </ul>
            </div>
        `;
  }

  // Regions
  if (icp.regions && icp.regions.length > 0) {
    html += `
            <div class="icp-item">
                <h4>Regions</h4>
                <ul>
                    ${icp.regions.map((reg) => `<li>${reg}</li>`).join("")}
                </ul>
            </div>
        `;
  }

  // Company Sizes
  if (icp.company_sizes && icp.company_sizes.length > 0) {
    html += `
            <div class="icp-item">
                <h4>Company Sizes</h4>
                <ul>
                    ${icp.company_sizes
                      .map((size) => `<li>${size}</li>`)
                      .join("")}
                </ul>
            </div>
        `;
  }

  // Pain Points
  if (icp.pain_points && icp.pain_points.length > 0) {
    html += `
            <div class="icp-item">
                <h4>Pain Points</h4>
                <ul>
                    ${icp.pain_points
                      .map((pain) => `<li>${pain}</li>`)
                      .join("")}
                </ul>
            </div>
        `;
  }

  // Root Keywords
  if (keywords.root && keywords.root.length > 0) {
    html += `
            <div class="icp-item">
                <h4>Root Keywords</h4>
                <ul>
                    ${keywords.root.map((kw) => `<li>${kw}</li>`).join("")}
                </ul>
            </div>
        `;
  }

  // Long-tail Keywords
  if (keywords.long_tail && keywords.long_tail.length > 0) {
    html += `
            <div class="icp-item">
                <h4>Long-tail Keywords</h4>
                <ul>
                    ${keywords.long_tail.map((kw) => `<li>${kw}</li>`).join("")}
                </ul>
            </div>
        `;
  }

  html += "</div>";
  container.innerHTML = html;
}

// Display Search Queries
function displayQueries(queryData) {
  const container = document.getElementById("queryResults");
  const queries = queryData.queries || queryData;

  let html = "";

  for (const [channel, channelQueries] of Object.entries(queries)) {
    if (channelQueries && channelQueries.length > 0) {
      html += `
                <div class="query-channel">
                    <h4>${channel}</h4>
                    <ul>
                        ${channelQueries
                          .map((query) => `<li>${query}</li>`)
                          .join("")}
                    </ul>
                </div>
            `;
    }
  }

  container.innerHTML = html;
}

// Display Copy Variants
function displayCopy(containerId, copyData) {
  const container = document.getElementById(containerId);
  const variants = copyData.variants || [];

  let html = "";

  variants.forEach((variant) => {
    html += `
            <div class="variant-card">
                <h4>Variant ${variant.variant}</h4>
                <div class="copy-text">${variant.copy}</div>
                <span class="tone-badge">${variant.tone || "N/A"}</span>
            </div>
        `;
  });

  container.innerHTML = html;
}

// Display Policy Review
function displayPolicyReview(policyData) {
  const container = document.getElementById("policyResults");

  let html = "";

  for (const [channel, review] of Object.entries(policyData)) {
    const statusClass =
      review.status === "pass"
        ? "status-pass"
        : review.status === "fail"
        ? "status-fail"
        : "status-needs-revision";

    html += `
            <div class="variant-card">
                <h4>${channel.toUpperCase()}</h4>
                <span class="status-badge ${statusClass}">
                    ${review.status.toUpperCase().replace("_", " ")}
                </span>
                ${
                  review.reasons && review.reasons.length > 0
                    ? `
                    <div style="margin-top: 15px;">
                        <strong>Issues:</strong>
                        <ul style="margin-top: 10px; padding-left: 20px;">
                            ${review.reasons
                              .map((reason) => `<li>${reason}</li>`)
                              .join("")}
                        </ul>
                    </div>
                `
                    : ""
                }
            </div>
        `;
  }

  container.innerHTML = html;
}
