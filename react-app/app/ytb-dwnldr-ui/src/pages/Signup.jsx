import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../utils/Session.js';
import Lottie from "lottie-react";
import successAnimation from "../../public/success.json";


function Signup() {
  const navigate = useNavigate()
  const [username, setUserName] = useState('')
  const [password, setPassword] = useState('')
  const [signupError, setSignupError] = useState('')
  const [signupSuccess, setSignupSuccess] = useState('')
  const { handleNavigation } = useAuth();
  const [successAnimationState, setSuccessAnimationState] = useState(false)
  useEffect(() => {
    fetchJwtToken();
  }, []);

  const fetchJwtToken = () => {
    const jwt_token = JSON.parse(localStorage.getItem('jwt_token'))
    if (jwt_token) {
      navigate('/home')
    }
  }

  const handleSignup = async (e) => {
    e.preventDefault()
    setSignupError('');
    setSignupSuccess('');
    try {
      const apiHost = import.meta.env.VITE_API_HOST;
      const apiPort = import.meta.env.VITE_API_PORT;
      const apiVersion = import.meta.env.VITE_API_VERSION;
      const apiSignup = import.meta.env.VITE_API_SIGNUP;
      const response = await axios.post(`http://${apiHost}:${apiPort}/${apiVersion}/${apiSignup}`, {
        username,
        password,
      })
      console.log('Signup Success:', response.data)
      setSignupSuccess('Signup Success:')
      localStorage.setItem('jwt_token', JSON.stringify(response.data))
      setSuccessAnimationState(true)
      setTimeout(() => {
        navigate('/home')
      }, 1500)
    } catch (err) {
      console.error('Signup Failed:', err.response?.data?.message || err.message)
      const message = err.response?.data?.message || err.response?.data?.errors || err.message;
      setSignupError(message);
    }
  }

  return (
    <form className="container mt-5 p-4 border rounded shadow-sm" style={{ maxWidth: '400px' }} onSubmit={handleSignup}>
      <h2 className="text-center mb-4">Signup</h2>
      <div className="mb-3">
      <input type="text" placeholder="Username" value={username} onChange={(e) => setUserName(e.target.value)} required />
      </div>
      <div className="mb-3">
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </div>
      {signupError && <div className="alert alert-danger py-1">{signupError}</div>}
      <div className="d-flex justify-content-between">
        {/* {signupSuccess && <div className="alert alert-success py-1">{signupSuccess}</div>} */}
        {successAnimationState ? <Lottie animationData={successAnimation} loop={true} style={{ width: 80, height: 80 }} /> :
        <>
          <button type="submit" className="btn btn-primary">Signup</button>
          <button className="btn btn-outline-secondary" onClick={() => {
            handleNavigation('login');
          }}>login</button>
        </>}
        
      </div>
    </form>
  )
}

export default Signup
