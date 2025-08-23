# Redis Caching Implementation Guide

This document outlines the Redis caching implementation for both the Mult-Tenant and Tenant Pharmacy services.

## Overview

Redis has been integrated as a high-performance caching layer to improve application performance and reduce database load. The implementation includes:

- **Database query results caching**
- **Session storage**
- **API response caching**
- **Template fragment caching**
- **Automatic query caching with django-cacheops**

## Architecture

### Mult-Tenant Service
- **Redis Port**: 6379
- **Memory Limit**: 256MB
- **Cache Aliases**: default, session, api
- **Key Prefix**: `mult_tenant`

### Tenant Pharmacy Service
- **Redis Port**: 6380 (to avoid conflicts)
- **Memory Limit**: 512MB
- **Cache Aliases**: default, session, api, inventory
- **Key Prefix**: `pharmacy`

## Configuration Files

### Docker Compose Updates

Both services now include Redis containers with:
- Persistent data storage
- Memory management with LRU eviction
- Health checks and restart policies
- Network isolation

### Redis Configuration Files

- `mult-tenant/redis.conf` - Optimized for mult-tenant caching
- `tenant_pharmacy/redis.conf` - Optimized for pharmacy-specific caching

### Django Settings

Redis caching is configured in Django settings with:
- Multiple cache aliases for different use cases
- Connection pooling and timeout settings
- Compression for large objects
- Automatic cache invalidation

## Cache Aliases and Use Cases

### Default Cache
- **Purpose**: General application caching
- **Timeout**: 5 minutes
- **Use Cases**: Frequently accessed data, computed values

### Session Cache
- **Purpose**: User session storage
- **Timeout**: 24 hours
- **Use Cases**: User authentication, session data

### API Cache
- **Purpose**: API response caching
- **Timeout**: 10 minutes
- **Use Cases**: REST API responses, external API calls

### Inventory Cache (Pharmacy Service Only)
- **Purpose**: Medication inventory data
- **Timeout**: 30 minutes
- **Use Cases**: Stock levels, medication availability

## Implementation Examples

### Basic Cache Usage

```python
from django.core.cache import cache

def get_user_profile(user_id):
    cache_key = f"user_profile:{user_id}"
    
    # Try to get from cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Fetch from database if not in cache
    profile_data = fetch_from_database(user_id)
    
    # Store in cache for 30 minutes
    cache.set(cache_key, profile_data, timeout=1800)
    return profile_data
```

### View-level Caching

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def cached_api_view(request):
    # This view will be cached for 15 minutes
    return JsonResponse(data)
```

### Using Specific Cache Aliases

```python
from django.core.cache import cache

def get_api_data():
    api_cache = cache.caches['api']
    cache_key = "api_data:latest"
    
    cached_data = api_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Fetch and cache data
    api_data = fetch_api_data()
    api_cache.set(cache_key, api_data)
    return api_data
```

## Cache Invalidation Strategies

### 1. Time-based Expiration
- Set appropriate timeouts based on data volatility
- Use shorter timeouts for frequently changing data
- Use longer timeouts for static data

### 2. Manual Invalidation
```python
def update_user_profile(user_id, new_data):
    # Update database
    user = User.objects.get(id=user_id)
    user.update(new_data)
    
    # Invalidate cache
    cache_key = f"user_profile:{user_id}"
    cache.delete(cache_key)
```

### 3. Version-based Invalidation
```python
def get_tenant_config(tenant_id, version=None):
    if version is None:
        version = cache.get(f"tenant_config_version:{tenant_id}", 1)
    
    cache_key = f"tenant_config:{tenant_id}:v{version}"
    return cache.get(cache_key)
```

## Performance Optimization

### 1. Connection Pooling
- Configured with max 50 connections
- Automatic retry on timeout
- Socket timeout settings

### 2. Compression
- Zlib compression for large objects
- Reduces memory usage and network transfer

### 3. Memory Management
- LRU eviction policy
- Memory limits per service
- Automatic cleanup of expired keys

## Monitoring and Statistics

### Redis INFO Command
Monitor Redis performance with:
```bash
# Connect to Redis CLI
docker exec -it redis_mult_tenant redis-cli
# or
docker exec -it redis_pharmacy redis-cli

# Get statistics
INFO memory
INFO stats
INFO keyspace
```

### Cache Hit/Miss Monitoring
Implement cache statistics in your application:
```python
def get_cache_stats():
    # Implement Redis INFO command parsing
    # Track cache hits, misses, and memory usage
    pass
```

## Best Practices

### 1. Cache Key Design
- Use descriptive, hierarchical keys
- Include version numbers for cache invalidation
- Use consistent naming conventions

### 2. Timeout Selection
- **Static data**: 24 hours or more
- **Configuration data**: 1 hour
- **User data**: 30 minutes
- **Session data**: 24 hours
- **API responses**: 10-15 minutes
- **Inventory data**: 30 minutes

### 3. Cache Size Management
- Monitor memory usage
- Set appropriate memory limits
- Use LRU eviction for automatic cleanup

### 4. Error Handling
- Implement fallback mechanisms
- Use `IGNORE_EXCEPTIONS` for graceful degradation
- Log cache errors for debugging

## Deployment

### 1. Environment Variables
Set these environment variables in your `.env` files:

```bash
# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379  # or 6380 for pharmacy service
REDIS_DB=0
```

### 2. Docker Compose
Start services with:
```bash
# Mult-tenant service
cd mult-tenant
docker-compose up -d

# Pharmacy service
cd tenant_pharmacy
docker-compose up -d
```

### 3. Health Checks
Monitor Redis health:
```bash
# Check Redis status
docker exec redis_mult_tenant redis-cli ping
docker exec redis_pharmacy redis-cli ping
```

## Troubleshooting

### Common Issues

1. **Connection Timeouts**
   - Check network connectivity
   - Verify Redis container is running
   - Check firewall settings

2. **Memory Issues**
   - Monitor memory usage
   - Adjust memory limits
   - Review cache timeouts

3. **Cache Misses**
   - Verify cache keys
   - Check cache invalidation logic
   - Monitor cache statistics

### Debug Commands

```bash
# Check Redis logs
docker logs redis_mult_tenant
docker logs redis_pharmacy

# Monitor Redis in real-time
docker exec -it redis_mult_tenant redis-cli monitor

# Check memory usage
docker exec -it redis_mult_tenant redis-cli info memory
```

## Security Considerations

1. **Network Security**
   - Redis containers are isolated in Docker networks
   - No direct external access by default

2. **Authentication**
   - Consider enabling Redis authentication for production
   - Use strong passwords

3. **Data Protection**
   - Sensitive data should not be cached
   - Implement proper data encryption if needed

## Future Enhancements

1. **Redis Cluster**
   - Implement Redis clustering for high availability
   - Add Redis Sentinel for failover

2. **Cache Warming**
   - Implement cache warming strategies
   - Pre-populate frequently accessed data

3. **Advanced Monitoring**
   - Integrate with Prometheus/Grafana
   - Implement cache performance alerts

4. **Cache Patterns**
   - Implement cache-aside patterns
   - Add write-through caching strategies

## Conclusion

This Redis caching implementation provides a robust foundation for improving application performance. The multi-alias approach allows for fine-grained control over different types of data, while the configuration is optimized for each service's specific needs.

For production deployment, consider implementing additional monitoring, security measures, and high-availability configurations based on your specific requirements.
