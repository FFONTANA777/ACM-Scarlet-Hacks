import { useEffect, useRef } from "react";
import Model from "./PetModel";

export default function ARCamera({ emotion, onClose }) {
  const videoRef = useRef();

  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "environment" }, audio: false })
      .then(stream => { videoRef.current.srcObject = stream; });

    return () => videoRef.current?.srcObject?.getTracks().forEach(t => t.stop());
  }, []);

  return (
    <div className="ar-overlay">
      <video ref={videoRef} autoPlay playsInline muted className="ar-video" />

      <div className="ar-pet">
        <Model emotion={emotion} />
      </div>

      <div className="ar-shadow" />

      <button className="ar-close" onClick={onClose}>✕ Exit AR</button>
    </div>
  );
}