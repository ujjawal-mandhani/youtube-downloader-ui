import { useNavigate } from 'react-router-dom';

export const useAuth = () => {
  const navigate = useNavigate();

  const handleLogOut = () => {
    localStorage.removeItem('jwt_token');
    navigate('/login');
  };

  const handleNavigation = (navigateArg) => {
    console.log(navigateArg);
    navigate(`/${navigateArg}`);
  };

  return { handleLogOut, handleNavigation };
};