import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

import Navbar from './Navbar'
import HeroSection from './HeroSection'
import FeaturesSection from './FeaturesSection'
import ArchitectureSection from './ArchitectureSection'
import CTASection from './CTASection'
import LandingFooter from './LandingFooter'

gsap.registerPlugin(ScrollTrigger)

const ANIMATED_SELECTORS = [
  '.hero-badge', '.hero-title-line', '.hero-subtitle',
  '.hero-buttons', '.hero-stat', '.orb-1', '.orb-2', '.orb-3',
  '.feature-card', '.features-header', '.arch-card', '.tech-pill', '.cta-content',
]

export default function Landing() {
  const navRef = useRef(null)
  const heroRef = useRef(null)
  const featuresRef = useRef(null)
  const archRef = useRef(null)
  const ctaRef = useRef(null)

  useEffect(() => {
    gsap.killTweensOf([navRef.current, ...ANIMATED_SELECTORS])
    gsap.set(ANIMATED_SELECTORS, { clearProps: 'all' })

    const ctx = gsap.context(() => {
      // Navbar
      gsap.fromTo(navRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.4, ease: 'power1.out' }
      )

      // Hero — simple fade up
      gsap.fromTo(['.hero-badge', '.hero-title-line', '.hero-subtitle', '.hero-buttons'],
        { y: 15, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5, stagger: 0.08, ease: 'power1.out', delay: 0.1 }
      )
      gsap.fromTo('.hero-stat',
        { opacity: 0 },
        { opacity: 1, duration: 0.4, stagger: 0.06, ease: 'power1.out', delay: 0.4 }
      )

      // Floating orbs (kept subtle)
      gsap.to('.orb-1', { y: -15, duration: 4, ease: 'sine.inOut', yoyo: true, repeat: -1 })
      gsap.to('.orb-2', { y: 10, duration: 5, ease: 'sine.inOut', yoyo: true, repeat: -1, delay: 1 })
      gsap.to('.orb-3', { y: -12, duration: 6, ease: 'sine.inOut', yoyo: true, repeat: -1, delay: 2 })

      // Features
      gsap.fromTo(['.features-header', '.feature-card'],
        { y: 15, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.4, stagger: 0.06, ease: 'power1.out', scrollTrigger: { trigger: featuresRef.current, start: 'top 85%' } }
      )

      // Architecture
      gsap.fromTo(['.arch-card', '.tech-pill'],
        { y: 15, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.4, stagger: 0.05, ease: 'power1.out', scrollTrigger: { trigger: archRef.current, start: 'top 85%' } }
      )

      // CTA
      gsap.fromTo('.cta-content',
        { y: 15, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.4, ease: 'power1.out', scrollTrigger: { trigger: ctaRef.current, start: 'top 85%' } }
      )
    })

    return () => ctx.revert()
  }, [])

  return (
    <div className="min-h-screen bg-[#fafafa] font-body overflow-x-hidden">
      <Navbar ref={navRef} />
      <HeroSection ref={heroRef} />
      <FeaturesSection ref={featuresRef} />
      <ArchitectureSection ref={archRef} />
      <CTASection ref={ctaRef} />
      <LandingFooter />
    </div>
  )
}
