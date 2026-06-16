import asyncio
import httpx
import time
import numpy as np

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def measure():
    signups = []
    logins = []
    
    # 1. Measure Signup
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(10):
            email = f"latency_test_{int(time.time() * 1000)}_{i}@example.com"
            t0 = time.perf_counter()
            r = await client.post(f"{BASE_URL}/auth/signup", json={
                "name": f"Test User {i}",
                "email": email,
                "password": "SuperPassword123!"
            })
            signups.append((time.perf_counter() - t0) * 1000)
            
            # 2. Measure Login
            t0 = time.perf_counter()
            r_login = await client.post(f"{BASE_URL}/auth/login", json={
                "email": email,
                "password": "SuperPassword123!"
            })
            logins.append((time.perf_counter() - t0) * 1000)
            
        print("--- Latency Measurements (ms) ---")
        print(f"Signup: Avg={np.mean(signups):.2f}ms | P95={np.percentile(signups, 95):.2f}ms")
        print(f"Login: Avg={np.mean(logins):.2f}ms | P95={np.percentile(logins, 95):.2f}ms")

if __name__ == "__main__":
    asyncio.run(measure())
