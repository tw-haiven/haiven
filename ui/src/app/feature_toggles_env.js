
const featureTogglesEnv = {
    DELIVERY_MANAGEMENT: process.env.NEXT_PUBLIC_FEATURE_DELIVERY_MANAGEMENT === 'true',
};

console.log('Feature Flags:', {
    DELIVERY_MANAGEMENT: featureTogglesEnv.DELIVERY_MANAGEMENT,
});

export default featureTogglesEnv;
