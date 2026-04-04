import Spline from '@splinetool/react-spline'
import { useRef, useEffect } from 'react'

const emotionMap = {
  normal: ['Body-normal'],
  sad:    ['Sad1', 'Sad2', 'Sad3'],
  tired:  ['Body-tired'],
  sleep:  ['Body-sleep'],
  sick:   ['Body-sick'],
}

const allBodies = ['Body-normal', 'Sad1', 'Sad2', 'Sad3', 'Body-tired', 'Body-sleep', 'Body-sick']

const applyEmotion = (spline, emotion) => {
  // move everything far below the scene
  allBodies.forEach(name => {
    const obj = spline.findObjectByName(name)
    if (obj) obj.position.y = -99999
  })

  // move current emotion back to y=0
  const targets = emotionMap[emotion] ?? emotionMap['normal']
  console.log(targets)
  targets.forEach(name => {
    const obj = spline.findObjectByName(name)
    if (obj) obj.position.y = 120
  })
}

export default function Model({ emotion = 'normal' }) {
  const splineRef = useRef()
  const source_URL = "https://prod.spline.design/kZEmqbz9dHggY13x/scene.splinecode"

  const onLoad = (spline) => {
    splineRef.current = spline
    
    // give Spline time to fully initialize objects
    setTimeout(() => {
      applyEmotion(spline, emotion)
    }, 500)
  }

  useEffect(() => {
    if (splineRef.current) {
      applyEmotion(splineRef.current, emotion)
    }
  }, [emotion])

  return (
    <Spline
      scene={source_URL}
      onLoad={onLoad}
      style={{ width: '100%', height: '100%' }}
    />
  )
}