import { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../utils/Session.js';
import Lottie from "lottie-react";
import successAnimation from "../../public/processing.json";

function Home() {
    const navigate = useNavigate()
    const jwt_token = JSON.parse(localStorage.getItem('jwt_token'))
    const [videoUrl, setVideoUrl] = useState('')
    const [videoDetails, setVideoDetails] = useState({})
    const [selectedIds, setSelectedIds] = useState({});
    const [fetchdetailsErr, setfetchdetailsErr] = useState('');
    const [successAnimationState, setSuccessAnimationState] = useState(false)
    const [downloadVideoError, setdownloadVideoError] = useState('')

    const { handleLogOut } = useAuth();
    
    const handleCheckboxChange = (id, data) => {
      setSelectedIds((prev) => {
        const prev_copy = {...prev}
        if(Object.prototype.hasOwnProperty.call(prev_copy, id)) {
          delete prev_copy[id];
        }
        else {
          prev_copy[id] = data;
        }
        return prev_copy;
      })
    }

    const downloadVideoFunc = async(e) => {
      e.preventDefault()
      setdownloadVideoError('')
      setSuccessAnimationState(true)
      const download_video_payload =  {
        "audio_video_formats": selectedIds,
        "title": videoDetails["title"],
        "jwt_token": jwt_token["token"],
        "video_url": videoUrl
      }
      console.log(download_video_payload)
      try {
        const apiHost = import.meta.env.VITE_API_HOST;
        const apiPort = import.meta.env.VITE_API_PORT;
        const apiVersion = import.meta.env.VITE_API_VERSION;
        const downloadVideo = import.meta.env.VITE_API_DOWNLOAD_VIDEO;
        const response = await axios.post(`http://${apiHost}:${apiPort}/${apiVersion}/${downloadVideo}`, download_video_payload, {
          responseType: 'blob' // Important: this tells axios to expect binary data
        })
        
        const blob = new Blob([response.data], { type: 'video/mp4' });
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${videoDetails["title"] || "download"}.mp4`;
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(downloadUrl);
        link.remove();

        console.log(':::::::::::::', response.data)
        navigate('/home')
      } catch (err) {
        const blob = err.response?.data;
        const text = await blob.text();
        const json = JSON.parse(text);
        // console.error('DownLoad Video Failed:', err.response?.data?.message || err.message)
        // const message = err.response?.data?.message || err.response?.data?.errors || err.message
        console.log(json.message)
        setdownloadVideoError(json.message)
      }
      setVideoDetails({})
      setSelectedIds({})
      setSuccessAnimationState(false)
    }

    const fetchVideoDetails = async (e) => {
      setSuccessAnimationState(true)
      setfetchdetailsErr('')
      setdownloadVideoError('')
      e.preventDefault()
      const token = jwt_token?.token
      const apiHost = import.meta.env.VITE_API_HOST;
      const apiPort = import.meta.env.VITE_API_PORT;
      const apiVersion = import.meta.env.VITE_API_VERSION;
      const fetchVideoUrl = import.meta.env.VITE_API_FETCH_VIDEO_DETAILS;
      try {
        const response = await axios.post(`http://${apiHost}:${apiPort}/${apiVersion}/${fetchVideoUrl}`, {
          video_url: videoUrl,
          jwt_token: token
        })
        setVideoDetails(response?.data?.message)
      }
      catch (err) {
        console.error('Fetching of Video Details Failed:', err.response?.data?.message || err.message)
        const message = err.response?.data?.message || err.response?.data?.errors || err.message
        // const responseCode = err.response.status
        console.log(message)
        // video_url is not in correct format
        console.log(err.response.status)
        if (message === "Token has expired") {
          console.log("Navigating to login Page")
          handleLogOut()
        } else{
          setfetchdetailsErr(message)
        }
      }
      setSuccessAnimationState(false)
    }
    return (
      <div className="container mt-5 p-4 border rounded shadow-sm bg-light" style={{ maxWidth: '1200px' }}>
        <form onSubmit={fetchVideoDetails}>
          <h2 className="text-center mb-4">🎬 Youtube & Instagram Downloader UI</h2>
          <div className="input-group mb-3">
          <input
            type="text"
            className="form-control"
            placeholder="Input Video URL"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            required
          />
          <button className="btn btn-primary" type="submit">Fetch Details</button>
          {successAnimationState && <Lottie animationData={successAnimation} speed={0.05} loop={true} style={{ width: 60, height: 60 }} />}
          </div>
          {fetchdetailsErr && <div className="alert alert-danger">{fetchdetailsErr}</div>}
          {downloadVideoError && <div className="alert alert-danger">{downloadVideoError}</div>}
        </form>
        {Object.keys(videoDetails).length > 0 && 
        <>
        <div className="mb-4"> Title Name: <span className="text-primary">{videoDetails?.title}</span></div>
          <form onSubmit={downloadVideoFunc}>
            <div className="table-responsive mb-3">
            <table className="table table-bordered table-hover align-middle">
              <thead className="table-light">
                <tr>
                  <th>Select Item</th>
                  <th>id</th>
                  <th>ext</th>
                  <th>resolution</th>
                </tr>
              </thead>
              <tbody>
              {Object.keys(videoDetails).map((item) => {
                if (!["subs", "title"].includes(item)) {
                  // console.log(item);
                  return (
                    <tr key={item}>
                    <td>
                      <input
                      type='checkbox'
                      checked={Object.prototype.hasOwnProperty.call(selectedIds, item)}
                      onChange={() => handleCheckboxChange(
                        item, {
                          "ext": videoDetails[item]?.ext, 
                          "resolution": videoDetails[item]?.resolution
                        })}
                      ></input>
                    </td>
                    <td>
                      {item}
                    </td>
                    <td>
                      {videoDetails[item]?.ext}
                    </td>
                    <td>
                      {videoDetails[item]?.resolution}
                    </td>
                  </tr>
                  )
                }
                return null;
              })}
              </tbody>
            </table>
            </div>
            <button type="submit" className="btn btn-success">Start Download Videos</button>
          </form>
          </>
        }
        <div className="d-flex mt-4 justify-content-between mb-4">
            <button className="btn btn-danger" onClick={handleLogOut}>Log Out</button>
            <button className="btn btn-secondary" onClick={()=> {
                navigate('/history')
            }}>History</button>
        </div>
        
      </div>
    )
  }
  
export default Home