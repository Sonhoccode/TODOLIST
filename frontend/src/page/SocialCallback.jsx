import { useEffect } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import api from "../api/client";

export default function SocialCallback() {
  const navigate = useNavigate();
  const { provider } = useParams(); // 'google' hoặc 'github'
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");

    if (!code) {
      navigate("/login", { replace: true });
      return;
    }

    if (provider === "google") {
      const savedState = sessionStorage.getItem("oauth_state_google");
      if (savedState && state && savedState !== state) {
        navigate("/login", { replace: true });
        return;
      }
    }

    if (provider === "github") {
      const savedState = sessionStorage.getItem("oauth_state_github");
      if (savedState && state && savedState !== state) {
        navigate("/login", { replace: true });
        return;
      }
    }

    const doSocialLogin = async () => {
      try {
        const redirectUri = `${window.location.origin}/auth/${provider}/callback`;

        const res = await api.post(`/auth/${provider}/`, {
          code,
          redirect_uri: redirectUri,
        });

        const token = res.data.key;
        if (token) {
          localStorage.setItem("token", token);
        }

        navigate("/home", { replace: true });
      } catch (error) {
        console.error("Social login error:", error);
        navigate("/login", { replace: true });
      }
    };

    doSocialLogin();
  }, [provider, searchParams, navigate]);

  return <div>Đang đăng nhập, vui lòng chờ...</div>;
}
