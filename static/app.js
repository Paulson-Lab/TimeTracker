let appData = {}; // Dictionary to store aggregated data for each application

// Function to start tracking
function startTracking() {
    const startButton = document.getElementById("startButton");
    startButton.classList.add("active-btn");
    startButton.innerText = "Tracking...";

    // Call the backend /start_tracking route
    fetch('/start_tracking', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log("Tracking started:", data);
        })
        .catch(error => {
            console.error('Error starting tracking:', error);
        });
}

// Function to stop tracking and retrieve aggregated data
function stopTracking() {
    const startButton = document.getElementById("startButton");
    startButton.classList.remove("active-btn");
    startButton.innerText = "Start Tracking";

    // Call the backend /stop_tracking route
    fetch('/stop_tracking', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log("Tracking stopped. Results:", data);
            aggregateResults(data); // Aggregate results on the frontend
        })
        .catch(error => {
            console.error('Error stopping tracking:', error);
        });
}

// Function to aggregate the results returned from the backend
function aggregateResults(data) {
    // Iterate over the data and aggregate results by application
    for (const [app, details] of Object.entries(data)) {
        if (appData[app]) {
            // If the application already exists, sum the values
            appData[app].time += details.time;
            appData[app].keystrokes += details.keystrokes;
            appData[app].mouse_clicks += details.mouse_clicks;
        } else {
            // Otherwise, create a new entry for the application
            appData[app] = {
                time: details.time,
                keystrokes: details.keystrokes,
                mouse_clicks: details.mouse_clicks,
            };
        }
    }
    displayResults(appData); // Display aggregated results
}

// Function to display results in the table
function displayResults(aggregatedData) {
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = "";

    if (Object.keys(aggregatedData).length === 0) {
        resultsContainer.innerHTML = '<p class="no-data">No data yet...</p>';
        return;
    }

    const clearIcon = document.createElement('i');
    clearIcon.classList.add('fas', 'fa-trash', 'clear-icon');
    clearIcon.onclick = clearTracking; // Attach the clearTracking function to icon
    resultsContainer.appendChild(clearIcon);

    let table = document.createElement("table");
    let header = table.createTHead();
    let headerRow = header.insertRow(0);
    headerRow.innerHTML = `<th>Application</th><th>Total Time Spent (s)</th><th>Total Keystrokes</th><th>Total Mouse Clicks</th>`;

    let tbody = table.createTBody();
    for (const [app, details] of Object.entries(aggregatedData)) {
        let row = tbody.insertRow();
        row.innerHTML = `<td title="${app}">${app}</td><td>${details.time.toFixed(2)}</td><td>${details.keystrokes}</td><td>${details.mouse_clicks}</td>`;
    }

    resultsContainer.appendChild(table);
}

// Function to clear the tracking results and reset
function clearTracking() {
    // Reset the results and the appData dictionary
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = '<p class="no-data">No data yet...</p>';
    appData = {}; // Clear the aggregated data
    const startButton = document.getElementById("startButton");
    startButton.classList.remove("active-btn");
    startButton.innerText = "Start Tracking";
    console.log("Tracking cleared.");
}
