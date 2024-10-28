document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;
    
    try {
        const response = await fetch('https://puc1.paulogontijo.com:5000/api/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                email,
                password,
                remember
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Signup successful!');
            // Redirect or do something else after successful signup
        } else {
            alert(data.error || 'Signup failed');
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during signup');
    }
});
