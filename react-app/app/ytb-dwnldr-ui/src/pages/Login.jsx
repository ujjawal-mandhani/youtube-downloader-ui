import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../utils/Session.js';
import Lottie from "lottie-react";
import successAnimation from "../../public/success.json";


function Login() {
  const navigate = useNavigate()
  const [username, setUserName] = useState('')
  const [password, setPassword] = useState('')
  const [loginError, setLoginError] = useState('')
  const [loginSuccess, setLoginSuccess] = useState('')
  const [successAnimationState, setSuccessAnimationState] = useState(false)
  useEffect(() => {
    fetchJwtToken();
  }, []);
  const { handleNavigation } = useAuth();
  const fetchJwtToken = () => {
    const jwt_token = JSON.parse(localStorage.getItem('jwt_token'))
    if (jwt_token) {
      navigate('/home')
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoginError('')
    setLoginSuccess('')
    try {
      const apiHost = import.meta.env.VITE_API_HOST;
      const apiPort = import.meta.env.VITE_API_PORT;
      const apiVersion = import.meta.env.VITE_API_VERSION;
      const apiLogin = import.meta.env.VITE_API_LOGIN;
      const response = await axios.post(`http://${apiHost}:${apiPort}/${apiVersion}/${apiLogin}`, {
        username,
        password,
      })
      console.log('Login Success:', response.data)
      setLoginSuccess("Signup Successfully")
      localStorage.setItem('jwt_token', JSON.stringify(response.data))
      setSuccessAnimationState(true)
      setTimeout(() => {
        navigate('/home')
      }, 1500)
    } catch (err) {
      console.error('Login Failed:', err.response?.data?.message || err.message)
      const message = err.response?.data?.message || err.response?.data?.errors || err.message
      setLoginError(message)
    }
  }

  return (
    <form onSubmit={handleLogin} className="container mt-5 p-4 border rounded shadow-sm" style={{ maxWidth: '400px' }}>
      <h2 className="text-center mb-4">Login</h2>
      <div className="mb-3">
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUserName(e.target.value)}
        required
      />
      </div>
      <div className="mb-3">
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      </div>
      {loginError && <div className="alert alert-danger py-1">{loginError}</div>}
      <div className="d-flex justify-content-between">
      {/* {loginSuccess && <div className="alert alert-success py-1">{loginSuccess}</div>} */}
      {
        successAnimationState ? <Lottie animationData={successAnimation} loop={true} style={{ width: 80, height: 80 }} /> : <>
          <button type="submit" className="btn btn-primary">Login</button>
          <button className="btn btn-outline-secondary" onClick={() => {
            handleNavigation('signup');
          }}>Signup</button>
        </>
      }
      </div>
    </form>
  )
}

export default Login
