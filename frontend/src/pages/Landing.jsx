import { LANDING_STYLES, Hero, StatsBand, Features, HowItWorks, WhySkillPath, CtaSection, Footer } from '../components/landing';

const Landing = ({ openAuthModal }) => {
  return (
    <div className="landing-root">
      <style>{LANDING_STYLES}</style>

      <Hero openAuthModal={openAuthModal} />

      <div className="mc-divider" />

      <StatsBand />

      <div className="mc-divider" />

      <Features />
      <HowItWorks />
      <WhySkillPath />
      <CtaSection openAuthModal={openAuthModal} />
      <Footer openAuthModal={openAuthModal} />
    </div>
  );
};

export default Landing;
