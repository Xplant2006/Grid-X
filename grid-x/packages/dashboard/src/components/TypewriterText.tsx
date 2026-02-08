'use client';

import { useState, useEffect } from 'react';
import styles from './typewriter.module.css';

interface TypewriterTextProps {
    text: string;
    speed?: number;
    delay?: number;
    showCursor?: boolean;
}

export default function TypewriterText({
    text,
    speed = 50,
    delay = 0,
    showCursor = true
}: TypewriterTextProps) {
    const [displayedText, setDisplayedText] = useState('');
    const [isStarted, setIsStarted] = useState(false);

    useEffect(() => {
        const timeout = setTimeout(() => {
            setIsStarted(true);
        }, delay);
        return () => clearTimeout(timeout);
    }, [delay]);

    useEffect(() => {
        if (!isStarted) return;

        setDisplayedText('');
        let index = 0;
        const interval = setInterval(() => {
            if (index < text.length) {
                setDisplayedText((prev) => prev + text.charAt(index));
                index++;
            } else {
                clearInterval(interval);
            }
        }, speed);

        return () => clearInterval(interval);
    }, [text, speed, isStarted]);

    return (
        <span className={styles.wrapper}>
            {displayedText}
            {showCursor && <span className={styles.cursor}>|</span>}
        </span>
    );
}
