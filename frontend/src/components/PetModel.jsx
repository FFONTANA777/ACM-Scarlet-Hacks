import Spline from '@splinetool/react-spline';

export default function Model() {
  return (
    <div style={{ width: '100%', height: '500px' }}>
      <Spline scene="https://prod.spline.design/kZEmqbz9dHggY13x/scene.splinecode" />
    </div>
  );
}

// export default function Model({ emotion = 'normal' }) {
//   const splineRef = useRef()

//   const onLoad = (spline) => {
//     splineRef.current = spline
//     applyEmotion(spline, emotion)
//   }

//   useEffect(() => {
//     if (splineRef.current) {
//       applyEmotion(splineRef.current, emotion)
//     }
//   }, [emotion])

//   return (
//     <Spline
//       scene="YOUR_URL"
//       onLoad={onLoad}
//       style={{ width: '100%', height: '100%' }}
//     />
//   )
// }