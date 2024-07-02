function showData(dataType) {
    let endpoint = '';
    let bodyData = '';

    if (dataType === 'accounts' || dataType === 'books' || dataType === 'checking_log') {
        endpoint = '/fetch_data';
        bodyData = `data_type=${dataType}`;
    } else {
        endpoint = '/fetch_account_data';
        bodyData = `library_card_no=${dataType}`; // Assuming dataType holds the library card number in this case
    }

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            // Add CSRF token header if needed
        },
        body: bodyData
    })
    .then(response => response.json())
    .then(data => {
        if (Array.isArray(data)) {
            // This condition handles accounts, books, and checking_log which return arrays
            displayTableData(data);
        } else {
            // This condition handles specific account data which does not return an array
            displayAccountData(data);
        }
    })
    .catch(error => console.error('Error fetching data:', error));
}

function displayTableData(data) {
    let html = '<table>';
    if (data.length > 0) {
        html += '<tr>';
        // Create table headers
        Object.keys(data[0]).forEach(key => {
            html += `<th>${key}</th>`;
        });
        html += '</tr>';

        // Create table rows
        data.forEach(row => {
            html += '<tr>';
            Object.values(row).forEach(value => {
                html += `<td>${value}</td>`;
            });
            html += '</tr>';
        });
    } else {
        html += '<tr><td>No data available.</td></tr>';
    }
    html += '</table>';
    document.getElementById('data_display').innerHTML = html;
}

function displayAccountData(data) {
    let html = `<h2>Account Information:</h2>
                <table>
                    <tr><th>Library Card Number:</th><td>${data.library_card_no}</td></tr>
                    <tr><th>Balance:</th><td>${data.balance}</td></tr>
                </table>
                <h2>Books Checked Out:</h2>`;

    if (data.books && data.books.length > 0) {
        html += '<table><tr><th>Title</th><th>Date Checked Out</th></tr>';
        data.books.forEach(book => {
            html += `<tr><td>${book.title}</td><td>${book.date}</td></tr>`;
        });
        html += '</table>';
    } else {
        html += '<p>No books currently checked out.</p>';
    }

    document.getElementById('data_display').innerHTML = html;
}
