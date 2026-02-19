import React from 'react';
import styles from './StatusTracker.module.css';

interface StatusTrackerProps {
    status: string;
}

const STEPS = ['PLANNING', 'RESEARCHING', 'WRITING', 'REVIEWING', 'COMPLETED'];

export default function StatusTracker({ status }: StatusTrackerProps) {
    let currentIndex = STEPS.indexOf(status);

    if (status === 'STARTING') currentIndex = -1;
    if (status === 'NEEDS_REVISION') currentIndex = 3;
    if (status === 'FAILED') currentIndex = STEPS.length;

    return (
        <div className={styles.container}>
            {STEPS.map((step, index) => {
                let className = styles.step;
                if (index < currentIndex || status === 'COMPLETED') {
                    className += ` ${styles.completed}`;
                } else if (index === currentIndex) {
                    className += ` ${styles.active}`;
                }

                return (
                    <div key={step} className={className}>
                        <div className={styles.circleOuter}>
                            <div className={styles.circleInner}>
                                {/* Wrap content in generic container for CSS selection if needed, 
                                    but text/string is fine directly too. 
                                    Using span explicitly for centering targetting */}
                                <span>
                                    {index < currentIndex || status === 'COMPLETED' ? '✓' : index + 1}
                                </span>
                            </div>
                        </div>
                        <span className={styles.label}>{step}</span>
                    </div>
                );
            })}
        </div>
    );
}
