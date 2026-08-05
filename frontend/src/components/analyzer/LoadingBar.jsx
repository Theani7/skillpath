import { motion, AnimatePresence } from 'framer-motion';

const LoadingBar = ({ loading }) => {
  return (
            <AnimatePresence>
              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  style={{
                    position: 'absolute', top: 0, left: 0, width: '100%',
                    height: '3px', background: 'var(--indigo-100)',
                    overflow: 'hidden', zIndex: 10,
                  }}
                >
                  <motion.div
                    animate={{ x: ['-100%', '100%'] }}
                    transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }}
                    style={{
                      position: 'absolute', height: '100%', width: '40%',
                      background: 'var(--color-primary)',
                    }}
                  />
                </motion.div>
              )}
            </AnimatePresence>
  );
};

export default LoadingBar;
