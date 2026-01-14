/**
 * Chart utilities for stock visualization
 */

/**
 * Parse ISO date string to Date object
 * @param {string} dateStr - ISO format date string
 * @returns {Date} - JavaScript Date object
 */
function parseDate(dateStr) {
    return new Date(dateStr);
}

/**
 * Calculate smooth rolling trendline with crossing point detection
 * @param {Array<number>} data - Array of data points
 * @param {Array<string>} labels - Array of timestamp labels (ISO format)
 * @param {number} alarmMin - Minimum alarm threshold
 * @returns {Object} - Object with trendline, labels, crossing points, and trend direction
 */
function calculateTrendline(data, labels, alarmMin) {
    const n = data.length;
    if (n < 2) return {
        trendline: data,
        extendedLabels: labels,
        crossingPoints: [],
        trendDirection: 'stable'
    };

    const windowSize = 3;
    const trendline = [];

    // Calculate trendline using rolling window approach for smooth transitions
    for (let i = 0; i < n; i++) {
        const windowStart = Math.max(0, i - Math.floor(windowSize / 2));
        const windowEnd = Math.min(n, windowStart + windowSize);
        const actualWindowStart = Math.max(0, windowEnd - windowSize);

        const windowData = data.slice(actualWindowStart, windowEnd);
        const windowLength = windowData.length;

        if (windowLength < 2) {
            trendline.push(data[i]);
            continue;
        }

        // Calculate linear regression for this window
        let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
        for (let j = 0; j < windowLength; j++) {
            sumX += j;
            sumY += windowData[j];
            sumXY += j * windowData[j];
            sumXX += j * j;
        }

        const slope = (windowLength * sumXY - sumX * sumY) / (windowLength * sumXX - sumX * sumX);
        const intercept = (sumY - slope * sumX) / windowLength;
        const centerIndex = i - actualWindowStart;
        trendline.push(slope * centerIndex + intercept);
    }

    // Calculate overall trend direction from last window
    const lastWindowStart = Math.max(0, n - windowSize);
    const lastWindow = data.slice(lastWindowStart, n);
    let overallSlope = 0;

    if (lastWindow.length >= 2) {
        let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
        for (let i = 0; i < lastWindow.length; i++) {
            sumX += i;
            sumY += lastWindow[i];
            sumXY += i * lastWindow[i];
            sumXX += i * i;
        }
        overallSlope = (lastWindow.length * sumXY - sumX * sumY) / (lastWindow.length * sumXX - sumX * sumX);
    }

    let trendDirection = 'stable';
    if (overallSlope < -0.1) trendDirection = 'down';
    else if (overallSlope > 0.1) trendDirection = 'up';

    let extendedLabels = [...labels];
    let extendedTrendline = [...trendline];
    let crossingPoints = [];

    const lastTrendValue = trendline[n - 1];

    // Detect all crossings in the historical trendline data
    for (let i = 1; i < trendline.length; i++) {
        const prevValue = trendline[i - 1];
        const currValue = trendline[i];

        if ((prevValue > alarmMin && currValue <= alarmMin) || (prevValue < alarmMin && currValue >= alarmMin)) {
            const ratio = (alarmMin - prevValue) / (currValue - prevValue);
            const exactIndex = (i - 1) + ratio;

            crossingPoints.push({
                index: exactIndex,
                value: alarmMin
            });
        }
    }

    // Calculate average time between counts
    let avgMinutesBetweenCounts = 30;
    if (n >= 2) {
        try {
            const recentLabels = labels.slice(-Math.min(5, n));
            const timestamps = recentLabels.map(parseDate);

            let totalMinutes = 0;
            for (let i = 1; i < timestamps.length; i++) {
                totalMinutes += (timestamps[i] - timestamps[i-1]) / (1000 * 60);
            }
            avgMinutesBetweenCounts = totalMinutes / (timestamps.length - 1);
        } catch (e) {
            console.log('Could not parse timestamps, using default interval');
        }
    }

    // Fixed number of future points
    const maxFuturePoints = 3;

    // If trending downward, project the future
    if (overallSlope < 0) {
        const lastTimestamp = parseDate(labels[labels.length - 1]);

        for (let i = 1; i <= maxFuturePoints; i++) {
            const y = lastTrendValue + (overallSlope * i);
            extendedTrendline.push(y);
            const minutesAhead = Math.round(i * avgMinutesBetweenCounts);
            extendedLabels.push('+' + minutesAhead + 'min');
        }

        // Calculate where trendline crosses alarm minimum
        const exactCrossingPoint = (alarmMin - lastTrendValue) / overallSlope;
        const firstProjectedValue = lastTrendValue + overallSlope;
        const lastProjectedValue = lastTrendValue + (overallSlope * maxFuturePoints);

        const crossesFromAbove = lastTrendValue > alarmMin && lastProjectedValue < alarmMin;
        const crossesWithinWindow = exactCrossingPoint > 0 && exactCrossingPoint <= maxFuturePoints;

        if (crossesFromAbove && crossesWithinWindow) {
            crossingPoints.push({
                index: n - 1 + exactCrossingPoint,
                value: alarmMin
            });
        }
    }

    return {
        trendline: extendedTrendline,
        extendedLabels: extendedLabels,
        crossingPoints: crossingPoints,
        trendDirection: trendDirection
    };
}

/**
 * Create time-based chart data from labels
 * @param {Array<string>} labels - ISO format timestamp labels
 * @param {Array<number>} data - Data values
 * @returns {Array<Object>} - Array of {x, y} objects
 */
function createTimeSeriesData(labels, data) {
    return labels.map((label, index) => {
        if (label.startsWith('+')) return null;
        return {
            x: parseDate(label),
            y: data[index]
        };
    }).filter(point => point !== null);
}

/**
 * Create timestamps array including future predictions
 * @param {Array<string>} extendedLabels - Labels including future predictions
 * @param {string} lastActualLabel - Last actual timestamp label
 * @param {number} avgMinutes - Average minutes between counts
 * @returns {Array<Date>} - Array of Date objects
 */
function createTimestampsWithPredictions(extendedLabels, lastActualLabel, avgMinutes) {
    const lastTimestamp = parseDate(lastActualLabel);

    return extendedLabels.map((label) => {
        if (label.startsWith('+')) {
            const minutes = parseInt(label.replace('+', '').replace('min', ''));
            return new Date(lastTimestamp.getTime() + minutes * 60000);
        } else {
            return parseDate(label);
        }
    });
}

/**
 * Format date for display in crossing labels
 * @param {Date} date - Date object
 * @returns {string} - Formatted date string in European format (DD/MM HH:mm)
 */
function formatCrossingDate(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${day}/${month} ${hours}:${minutes}`;
}
