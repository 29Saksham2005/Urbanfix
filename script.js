// script.js
function signIn(userType) {
    const additionalContent = document.getElementById('additional-content');
    additionalContent.style.display = 'block'; // Show additional content

    // Clear any existing content
    additionalContent.innerHTML = '';

    if (userType === 'citizen') {
        additionalContent.innerHTML = `
            <h3>Citizen Sign In</h3>
            <form>
                <input type="text" placeholder="phone number"><br>
                <input type="password" placeholder="otp"><br>
                <button type="submit">Sign In</button>
            </form>
        `;
    } else if (userType === 'authority') {
        additionalContent.innerHTML = `
            <h3>Government Authority Sign In</h3>
            <form>
                <input type="text" placeholder="Authority ID"><br>
                <input type="password" placeholder="Password"><br>
                <button type="submit">Sign In</button>
            </form>
        `;
    } else if (userType === 'business') {
        additionalContent.innerHTML = `
            <h3>Local Business Sign In</h3>
            <form>
                <input type="text" placeholder="Business Registration Number"><br>
                <input type="password" placeholder="Password"><br>
                <button type="submit">Sign In</button>
            </form>
        `;
    }

    // Add event listeners for form submissions, etc. as needed
}