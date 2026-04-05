import Spline from '@splinetool/react-spline'
import { useRef, useEffect, useCallback } from 'react'

const emotionMap = {
  normal: ['Body-normal'],
  happy:  ['Body-normal'],
  sad:    ['Body-sad'],
  tired:  ['Body-tired'],
  sleep:  ['Body-sleep'],
  sick:   ['Body-sick'],
}

const allBodies = ['Body-normal', 'Body-sad', 'Body-tired', 'Body-sleep', 'Body-sick']

const applyEmotion = (spline, emotion) => {
  allBodies.forEach(name => {
    const obj = spline.findObjectByName(name)
    if (obj) obj.position.y = -99999
  })

  const targets = emotionMap[emotion] ?? emotionMap['normal']
  targets.forEach(name => {
    const obj = spline.findObjectByName(name)
    if (obj) obj.position.y = 120
  })
}

export default function Model({ emotion = 'normal' }) {
  const splineRef = useRef()
  const emotionRef = useRef(emotion)
  const source_URL = "https://prod.spline.design/kZEmqbz9dHggY13x/scene.splinecode"

  const onLoad = useCallback((spline) => {
    splineRef.current = spline
    setTimeout(() => {
      applyEmotion(spline, emotionRef.current)
    }, 500)
  }, [])

  useEffect(() => {
    emotionRef.current = emotion
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
