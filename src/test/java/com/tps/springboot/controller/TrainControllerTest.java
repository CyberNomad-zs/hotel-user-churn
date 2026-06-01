package com.tps.springboot.controller;

import com.tps.springboot.common.Result;
import com.tps.springboot.service.ITrainService;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.assertEquals;

class TrainControllerTest {

    @Test
    void beginTrainReturnsServiceFailure() throws Exception {
        TrainController controller = new TrainController();
        ITrainService trainService = Mockito.mock(ITrainService.class);
        StringRedisTemplate redisTemplate = Mockito.mock(StringRedisTemplate.class);
        Result failure = Result.error("507", "训练失败");
        Mockito.when(trainService.train("bad.csv", "modelRF")).thenReturn(failure);
        ReflectionTestUtils.setField(controller, "trainService", trainService);
        ReflectionTestUtils.setField(controller, "stringRedisTemplate", redisTemplate);

        Result result = controller.beginTrain("bad.csv", "modelRF");

        assertEquals("507", result.getCode());
        assertEquals("训练失败", result.getMsg());
    }
}
