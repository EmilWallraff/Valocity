import { useEffect } from 'react';

function Login() {
    useEffect(() => {
      document.title = 'Login - valocity.gg';
    }, []);

    return (
      <div>
        <h2>Login</h2>
        <form>
          <input type="text" placeholder="Username" /><br />
          <input type="password" placeholder="Password" /><br />
          <button>Log In</button>
        </form>
      </div>
    );
  }
  
  export default Login;
  