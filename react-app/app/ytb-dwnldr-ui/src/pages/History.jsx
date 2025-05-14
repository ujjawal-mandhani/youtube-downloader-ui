import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../utils/Session.js';

function History() {
    const navigate = useNavigate()
    const jwt_token = JSON.parse(localStorage.getItem('jwt_token'))
    const [activities, setActivities] = useState([]);
    const [activitySkip, setActivitySkip] = useState(0);

    const { handleLogOut } = useAuth();

    const apiHost = import.meta.env.VITE_API_HOST;
    const apiPort = import.meta.env.VITE_API_PORT;
    const apiVersion = import.meta.env.VITE_API_VERSION;
    const fetchUserHistory = import.meta.env.VITE_API_FETCH_USER_HISTORY;
    useEffect(() => {
        axios.post(`http://${apiHost}:${apiPort}/${apiVersion}/${fetchUserHistory}`, {
            "jwt_token": jwt_token["token"],
            "limit": "10",
            "skip": String(activitySkip)
        })
          .then(res => {
            console.log(res.data)
            if (activitySkip === 0) {
                setActivities(res.data.message);
            } else {
                setActivities((prev_state) => {
                    const newState = [...prev_state, ...res.data.message]
                    return newState
                });
            }
          })
          .catch(err => {
            console.error('Error fetching activities:', err.response?.data?.message || err.message);
            const message = err.response?.data?.message || err.response?.data?.errors || err.message
            console.log(message)
          });
      }, [activitySkip]);
    return (
        <div className="container mt-5 p-4 border rounded shadow-sm bg-light" style={{ maxWidth: '90%' }}>
            <h2 className="text-center mb-4">History</h2>
            <div className="table-responsive mb-3">
            <table className="table table-bordered table-hover align-middle">
              <thead className="table-light">
                <tr>
                  <th>audit_timestamp</th>
                  <th>title</th>
                  <th>audio_id</th>
                  <th>video_id</th>
                  <th>video_url</th>
                  <th>download_video</th>
                </tr>
              </thead>
              <tbody>
            {activities && <>{activities.map((item) => {
                const audio_id = Object.entries(item.video_details.audio_video_formats).filter(([keys, values]) => {
                    return values.resolution === "audio only"
                }).map(([keys1, values1]) => {
                    return keys1
                })[0]

                const video_id = Object.entries(item.video_details.audio_video_formats).filter(([keys, values]) => {
                    return values.resolution !== "audio only"
                }).map(([keys1, values1]) => {
                    return keys1
                })[0]

                return (
                    <tr key={item._id.$oid}>
                        <td>
                            {item.audit_timestamp}
                        </td>
                        <td>
                            {item.video_details.title}
                        </td>
                        <td>
                            {audio_id}
                        </td>
                        <td>
                            {video_id}
                        </td>
                        <td>
                            <button className="btn btn-secondary" onClick={async() => {
                                const download_video_payload =  {
                                    ...item.video_details,
                                    "jwt_token": jwt_token["token"]
                                }
                                console.log(download_video_payload)
                                const apiHost = import.meta.env.VITE_API_HOST;
                                const apiPort = import.meta.env.VITE_API_PORT;
                                const apiVersion = import.meta.env.VITE_API_VERSION;
                                const downloadVideo = import.meta.env.VITE_API_DOWNLOAD_VIDEO;
                                console.log(`http://${apiHost}:${apiPort}/${apiVersion}/${downloadVideo}`)
                                const response = await axios.post(`http://${apiHost}:${apiPort}/${apiVersion}/${downloadVideo}`, download_video_payload, {
                                    responseType: 'blob'
                                })
                                const blob = new Blob([response.data], { type: 'video/mp4' });
                                const downloadUrl = window.URL.createObjectURL(blob);
                                const link = document.createElement('a');
                                link.href = downloadUrl;
                                link.download = `${download_video_payload.title || "download"}.mp4`;
                                document.body.appendChild(link);
                                link.click();
                                window.URL.revokeObjectURL(downloadUrl);
                                link.remove();
                                console.log(':::::::::::::', response.data)
                            }}>download again</button>
                        </td>
                        <td>
                            <a href={item.video_details.video_url} target="_blank" rel="noopener noreferrer">link</a>
                        </td>
                    </tr>
                )
            })}</>}
            </tbody>
            </table>
            </div>
            <div>
                <button className="btn btn-success" onClick={() => {
                    setActivitySkip((prev_state) => {
                        return prev_state + 10
                    })
                }}>Fetch More Activities</button>
            </div>
            <div className="d-flex mt-4 justify-content-between mb-4" >
            <button className="btn btn-danger" onClick={()=> {
                handleLogOut()
            }}>Logout</button>
            <button className="btn btn-secondary" onClick={()=> {
                navigate('/home')
            }}>Home</button>
            </div>
        </div>
    )
}

export default History